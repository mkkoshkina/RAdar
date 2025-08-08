import os
import pandas as pd
import subprocess
from utils import log_message

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
create_prs_table(
    sscore_vars_path="input/plink/lm5515_dedup.prs.sscore.vars",
    full_score_path="input/prs/PGS000195_hmPOS_GRCh37.txt",
    afreq_path="input/prs/PGS000195_hmPOS_GRCh37.freq",
    bfile_prefix="input/plink/lm5515_dedup",
    output_dir="output",
    clean_tmp_files=True
)