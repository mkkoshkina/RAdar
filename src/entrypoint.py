import os
import sys
import subprocess
from datetime import datetime

def log_message(msg, log_file=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    if log_file:
        with open(log_file, 'a') as f:
            f.write(log_msg + '\n')

def main():
    if len(sys.argv) < 3:
        print("Usage: python entrypoint.py <input_vcf> <assembly> [clean_tmp_files]")
        sys.exit(1)

    input_vcf = sys.argv[1]
    assembly = sys.argv[2]
    clean_tmp_files = sys.argv[3].lower() == "true" if len(sys.argv) > 3 else False

    # Choose PRS and FREQ files based on assembly
    if assembly == "GRCh38":
        prs_path = "input/prs/PGS000195_hmPOS_GRCh38.txt"
        freq_path = "input/prs/PGS000195_hmPOS_GRCh38.freq"
    elif assembly == "GRCh37":
        prs_path = "input/prs/PGS000195_hmPOS_GRCh37.txt"
        freq_path = "input/prs/PGS000195_hmPOS_GRCh37.freq"
    else:
        print(f"Unknown ASSEMBLY: {assembly}")
        sys.exit(1)

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
        sys.exit(1)
    log_message(f"VCF filtered in {(datetime.now() - step_start).total_seconds():.1f} seconds", log_file)

    # Step 2: Convert to PLINK
    log_message("Converting filtered VCF to PLINK format...", log_file)
    step_start = datetime.now()
    result = subprocess.run([
        'plink2', '--vcf', filtered_vcf, '--make-bed', '--out', plink_prefix
    ], capture_output=True, text=True)
    if result.returncode != 0:
        log_message(f"PLINK2 conversion failed: {result.stderr}", log_file)
        sys.exit(1)
    log_message(f"PLINK files created in {(datetime.now() - step_start).total_seconds():.1f} seconds", log_file)

    # Step 3: Remove duplicate variants
    log_message("Removing duplicate variants with PLINK2...", log_file)
    step_start = datetime.now()
    result = subprocess.run([
        'plink2', '--bfile', plink_prefix, '--rm-dup', 'force-first', '--make-bed', '--out', f"{plink_prefix}_dedup"
    ], capture_output=True, text=True)
    if result.returncode != 0:
        log_message(f"PLINK2 duplicate removal failed: {result.stderr}", log_file)
        sys.exit(1)
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
        sys.exit(1)
    log_message(f"PRS calculated in {(datetime.now() - step_start).total_seconds():.1f} seconds", log_file)

    # Step 5: Parse PLINK results to JSON
    log_message("Parsing PLINK results to JSON...", log_file)
    step_start = datetime.now()
    sscore_file = f"{plink_prefix}_dedup.prs.sscore"
    if not os.path.exists(sscore_file):
        log_message(f"PLINK sscore file not found: {sscore_file}", log_file)
        sys.exit(1)
    # You may need to adjust the import path for your parse_plink_res_to_json.py
    from parse_plink_res_to_json import parse_profile_file
    results = parse_profile_file(sscore_file)
    with open(output_json, "w") as f:
        f.write(results)
    log_message(f"JSON created in {(datetime.now() - step_start).total_seconds():.1f} seconds", log_file)

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
    log_message(f"Done. JSON output at {output_json}", log_file)
    log_message(f"Total runtime: {total_duration:.1f} seconds", log_file)

if __name__ == "__main__":
    main()