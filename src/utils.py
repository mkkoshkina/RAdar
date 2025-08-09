from datetime import datetime
import os
import subprocess
import json
import sys
import os
import pandas as pd
import subprocess
from pathlib import Path

def log_message(msg, log_file=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    if log_file:
        with open(log_file, 'a') as f:
            f.write(log_msg + '\n')
        
def parse_profile_file(input_path):
    with open(input_path) as f:
        lines = [line.strip() for line in f if line.strip()]
    if len(lines) < 2:
        raise ValueError("No data rows found in the file.")

    header = lines[0].split()
    records = []
    for line in lines[1:]:
        data = line.split()
        record = dict(zip(header, data))
        # Rename fields as requested
        out = {}
        for k, v in record.items():
            if k == "IID":
                out["id"] = v
            elif k == "ALLELE_CT":
                out["number_of_snps"] = int(v)
            elif k == "NAMED_ALLELE_DOSAGE_SUM":
                out["number_of_snps_used"] = int(v)
            elif k == "SCORE1_AVG":
                out["score"] = float(v)
        records.append(out)
    return json.dumps(records, indent=2)

def create_prs_table(
    sscore_vars_path,
    full_score_path,
    afreq_path,
    bfile_prefix,
    output_dir="output",
    clean_tmp_files=True
):
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, "create_table_with_used_snps.log")

    log_message("Starting PRS table creation pipeline", log_file)

    # 1. Subset score file using grep
    subset_score_path = os.path.join(output_dir, "subset_score.txt")
    grep_cmd = [
        "grep", "-Fwf", sscore_vars_path, full_score_path
    ]
    log_message(f"Running grep to subset score file: {' '.join(grep_cmd)}", log_file)
    with open(subset_score_path, "w") as out_f:
        result = subprocess.run(grep_cmd, stdout=out_f)
    if result.returncode != 0:
        log_message("grep command failed", log_file)
        raise RuntimeError("grep command failed")
    log_message(f"Subset score file created at {subset_score_path}", log_file)

    # 2. Extract genotypes using plink2
    plink_out_prefix = os.path.join(output_dir, "lm5515_dedup_prs_snpsVCF_BCF")
    plink_cmd = [
        "plink2", "--bfile", bfile_prefix,
        "--extract", sscore_vars_path,
        "--recode", "A",
        "--out", plink_out_prefix
    ]
    log_message(f"Running plink2 to extract genotypes: {' '.join(plink_cmd)}", log_file)
    result = subprocess.run(plink_cmd)
    if result.returncode != 0:
        log_message("plink2 command failed", log_file)
        raise RuntimeError("plink2 command failed")
    log_message(f"PLINK2 .raw file created at {plink_out_prefix + '.raw'}", log_file)

    # 3. Read subset_score.txt
    log_message("Reading subset score file", log_file)
    score_cols = [
        "rsID", "chr_name", "chr_position", "effect_allele", "other_allele", "effect_weight",
        "allelefrequency_effect", "is_haplotype", "imputation_method", "variant_type", "OR",
        "hm_source", "hm_rsID", "hm_chr", "hm_pos", "hm_inferOtherAllele", "hm_match_chr", "hm_match_pos"
    ]
    score = pd.read_csv(subset_score_path, sep="\t", header=None, names=score_cols, dtype=str)
    score = score[["rsID", "other_allele", "effect_allele", "effect_weight"]]
    score = score.rename(columns={
        "rsID": "rsid",
        "other_allele": "ref",
        "effect_allele": "effect_allele",
        "effect_weight": "effect_size"
    })
    score["effect_size"] = score["effect_size"].astype(float)

    # 4. Read .afreq (PLINK2 frequency file)
    log_message("Reading allele frequency file", log_file)
    afreq_cols = ["#CHROM", "POS", "ID", "REF", "ALT", "ALT_FREQS", "OBS_CT"]
    afreq = pd.read_csv(afreq_path, sep="\t", header=0, names=afreq_cols, dtype=str)
    afreq = afreq[["ID", "ALT_FREQS"]]

    # 5. Read .raw (PLINK2 genotype file)
    log_message("Reading PLINK2 .raw genotype file", log_file)
    raw_file = plink_out_prefix + ".raw"
    raw = pd.read_csv(raw_file, sep=r'\s+')
    genotype_cols = [col for col in raw.columns if col not in ["FID", "IID", "PAT", "MAT", "SEX", "PHENOTYPE"]]
    genotypes = raw.loc[0, genotype_cols].to_frame().reset_index()
    genotypes.columns = ["rsid", "genotype"]
    genotypes['rsid'] = genotypes['rsid'].str.split('_').str[0]

    # 6. Merge all
    log_message("Merging score, frequency, and genotype data", log_file)
    merged = score.merge(afreq, left_on="rsid", right_on="ID", how="left")
    merged = merged.merge(genotypes, on="rsid", how="left")
    merged.drop(columns="ID", inplace=True)

    # 7. Reorder columns
    merged = merged[["rsid", "ref", "effect_allele", "effect_size", "ALT_FREQS", "genotype"]]

    # 8. Save to file
    final_table_path = os.path.join(output_dir, "final_prs_table.tsv")
    merged.to_csv(final_table_path, sep="\t", index=False)
    log_message(f"Done! Output written to {final_table_path}", log_file)

    # 9. Clean up temporary files
    if clean_tmp_files:
        log_message("Cleaning up temporary files...", log_file)
        tmp_files = [
            subset_score_path,
            raw_file,
            plink_out_prefix + ".log",
            plink_out_prefix + ".nosex"
        ]
        for f in tmp_files:
            if os.path.exists(f):
                os.remove(f)
        log_message("Temporary files removed.", log_file)

    return merged

# Example usage:
# create_prs_table(
#     sscore_vars_path="input/plink/lm5515_dedup.prs.sscore.vars",
#     full_score_path="input/prs/PGS000195_hmPOS_GRCh37.txt",
#     afreq_path="input/prs/PGS000195_hmPOS_GRCh37.freq",
#     bfile_prefix="input/plink/lm5515_dedup",
#     output_dir="output",
#     clean_tmp_files=True
# )

def read_vcf_as_df(vcf_path: str) -> pd.DataFrame:
    # Grab real header (so we capture sample column names)
    with open(vcf_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("#CHROM"):
                header = line.lstrip("#").strip().split("\t")
                break
        else:
            header = ['CHROM','POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT', 'sample']
    
    if header[-1] != "sample":
        header[-1] = "sample"
    
    df = pd.read_csv(
        vcf_path,
        sep="\t",
        comment="#",
        names=header,
        dtype=str,
        engine="c",
    )
    if "#CHROM" in df.columns:
        df = df.rename(columns={"#CHROM": "CHROM"})

    df["ID"] = df["ID"].fillna("").str.lower()
    df.loc[~df["ID"].str.startswith("rs"), "ID"] = "rs" + df["ID"]

    return df

def intersect_vcf_with_tsv(vcf_path: str, tsv_path: str, out_csv: str) -> pd.DataFrame:
    # Read inputs
    vcf_df = read_vcf_as_df(vcf_path)

    ann = pd.read_csv(tsv_path, sep="\t", dtype=str).fillna("")
    # Normalize rsID case for safe join
    vcf_df["ID"] = vcf_df["ID"].str.strip().str.lower()
    ann["Variant"] = ann["Variant"].str.strip().str.lower()

    # If TSV can have duplicate rows per rsID, keep first (or change to aggregate if you prefer)
    ann = ann.drop_duplicates(subset=["Variant"], keep="first")

    merged = vcf_df.merge(
        ann,
        left_on="ID",
        right_on="Variant",
        how="inner",
        copy=False,
    )
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(out_csv, index=False)
    return merged

# Example usage:
#intersect_vcf_with_tsv("lm5515.vcf", "annotations.tsv", "intersection.csv")

def run_plink_pipeline(input_vcf, assembly='GRCh37', clean_tmp_files=True):
    # Set up paths
    if assembly == "GRCh38":
        prs_path = "input/prs/PGS000195_hmPOS_GRCh38.txt"
        freq_path = "input/prs/PGS000195_hmPOS_GRCh38.freq"
    elif assembly == "GRCh37":
        prs_path = "input/prs/PGS000195_hmPOS_GRCh37.txt"
        freq_path = "input/prs/PGS000195_hmPOS_GRCh37.freq"
    else:
        raise ValueError(f"Unknown ASSEMBLY: {assembly}")
    drug_annotations_path = "input\annotations\drug_toxicity_annotations.tsv"
    sample = os.path.basename(input_vcf).replace('.vcf', '')
    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{sample}.log")

    filtered_vcf = f"input/vcf/{sample}.filtered.vcf"
    plink_prefix = f"input/plink/{sample}"
    output_json = f"output/{sample}.json"

    os.makedirs("input/vcf", exist_ok=True)
    os.makedirs("input/plink", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    start_time = datetime.now()
    log_message("Script started", log_file)
    log_message(f"Input VCF: {input_vcf}", log_file)
    log_message(f"PRS file: {prs_path}", log_file)
    log_message(f"Clean temporary files: {clean_tmp_files}", log_file)

    # Step 1: Filter VCF
    log_message("Filtering VCF (removing variants with missing ID and sex chromosomes)...", log_file)
    step_start = datetime.now()
    result = subprocess.run([
        'bcftools', 'view', '-e', 'ID=="."', '-t', '^chrX,chrY,X,Y', '-m2', '-M2',
        input_vcf, '-o', filtered_vcf
    ], capture_output=True, text=True)
    if result.returncode != 0:
        log_message(f"BCFtools filtering failed: {result.stderr}", log_file)
        raise RuntimeError("BCFtools filtering failed")
    log_message(f"VCF filtered in {(datetime.now() - step_start).total_seconds():.1f} seconds", log_file)

    # Step 2: Convert to PLINK
    log_message("Converting filtered VCF to PLINK format...", log_file)
    step_start = datetime.now()
    result = subprocess.run([
        'plink2', '--vcf', filtered_vcf, '--make-bed', '--out', plink_prefix
    ], capture_output=True, text=True)
    if result.returncode != 0:
        log_message(f"PLINK2 conversion failed: {result.stderr}", log_file)
        raise RuntimeError("PLINK2 conversion failed")
    log_message(f"PLINK files created in {(datetime.now() - step_start).total_seconds():.1f} seconds", log_file)

    # Step 3: Remove duplicate variants
    log_message("Removing duplicate variants with PLINK2...", log_file)
    step_start = datetime.now()
    result = subprocess.run([
        'plink2', '--bfile', plink_prefix, '--rm-dup', 'force-first', '--make-bed', '--out', f"{plink_prefix}_dedup"
    ], capture_output=True, text=True)
    if result.returncode != 0:
        log_message(f"PLINK2 duplicate removal failed: {result.stderr}", log_file)
        raise RuntimeError("PLINK2 duplicate removal failed")
    log_message(f"Duplicates removed in {(datetime.now() - step_start).total_seconds():.1f} seconds", log_file)

    # Step 4: Calculate PRS
    log_message("Calculating PRS...", log_file)
    step_start = datetime.now()
    result = subprocess.run([
        'plink2', '--bfile', f"{plink_prefix}_dedup", '--read-freq', freq_path,
        '--score', prs_path, '1', '4', '6', 'header', 'list-variants',
        '--out', f"{plink_prefix}_dedup.prs"
    ], capture_output=True, text=True)
    if result.returncode != 0:
        log_message(f"PLINK2 PRS calculation failed: {result.stderr}", log_file)
        raise RuntimeError("PLINK2 PRS calculation failed")
    log_message(f"PRS calculated in {(datetime.now() - step_start).total_seconds():.1f} seconds", log_file)

    # Step 5: Table with used snps
    create_prs_table(
        sscore_vars_path=f"{plink_prefix}_dedup.prs.sscore.vars",
        full_score_path=prs_path,
        afreq_path=freq_path,
        bfile_prefix=f"{plink_prefix}_dedup",
        output_dir="output",
        clean_tmp_files=clean_tmp_files
    )

    #Step 5.5: Parse supplementary mutations
    intersect_vcf_with_tsv(input_vcf, drug_annotations_path, "output/intersection_with_drug_annotation.csv")

    # Step 6: Clean up
    if clean_tmp_files:
        log_message("Cleaning up temporary files...", log_file)
        temp_files = [
            filtered_vcf,
            f"{plink_prefix}.bed", f"{plink_prefix}.bim", f"{plink_prefix}.fam", f"{plink_prefix}.log", f"{plink_prefix}.nosex",
            f"{plink_prefix}_dedup.bed", f"{plink_prefix}_dedup.bim", f"{plink_prefix}_dedup.fam", f"{plink_prefix}_dedup.log",
            f"{plink_prefix}_dedup.prs.log", f"{plink_prefix}_dedup.prs.nosex", f"{plink_prefix}_dedup.prs.profile",
            f"{plink_prefix}_dedup.prs.sscore", f"{plink_prefix}_dedup.prs.sscore.vars"
        ]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        log_message("Temporary files removed", log_file)

    total_duration = (datetime.now() - start_time).total_seconds()
    log_message(f"Done. Output at {output_json}", log_file)
    log_message(f"Total runtime: {total_duration:.1f} seconds", log_file)
    return {"status": "success", "output_json": output_json, "log_file": log_file, "table_snps_used" : "output/final_prs_table.tsv"}


# run_plink_pipeline(
#     input_vcf='/Users/m.trofimov/Dropbox/Study/bioinf_hackathon/2025/arthritis_prs/RAdar/input/vcf/lm5515.vcf',
#     assembly='GRCh37'
# )