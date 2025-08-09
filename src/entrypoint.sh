#!/bin/bash

INPUT_VCF=$1      # e.g., input/vcf/ng1657.hg38.vcf
ASSEMBLY=$2       # e.g., GRCh38 or GRCh37
# PRS_PATH_PREFIX=$3       # e.g., input/prs/PGS002769_hmPOS
CLEAN_TMP_FILES=${3:-true}  # true/false, default to false
# Set ASSEMBLY variable (you can pass it as an argument or set it before running the script)

# Choose PRS file based on ASSEMBLY
if [ "$ASSEMBLY" = "GRCh38" ]; then
    PRS_PATH="input/prs/PGS000195_hmPOS_GRCh38.txt"
    FREQ_PATH="input/prs/PGS000195_hmPOS_GRCh38.freq"
elif [ "$ASSEMBLY" = "GRCh37" ]; then
    PRS_PATH="input/prs/PGS000195_hmPOS_GRCh37.txt"
    FREQ_PATH="input/prs/PGS000195_hmPOS_GRCh37.freq"
else
    echo "Unknown ASSEMBLY: $ASSEMBLY"
    exit 1
fi

# Extract sample name (basename without .hg38.vcf)
sample=$(basename "$INPUT_VCF" .vcf)

# Define log file path
LOG_DIR="log"
LOG_FILE="${LOG_DIR}/${sample}.log"
mkdir -p "$LOG_DIR"

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

START_TIME=$(date +%s)
log "Script started"
log "Input VCF: $INPUT_VCF"
log "PRS file: $PRS_PATH"
log "Clean temporary files: $CLEAN_TMP_FILES"

# Extract sample name (basename without .hg38.vcf)
# sample=$(basename "$INPUT_VCF" .hg38.vcf)

# Define paths
FILTERED_VCF="input/vcf/${sample}.filtered.vcf"
PLINK_PREFIX="input/plink/${sample}"
OUTPUT_JSON="output/${sample}.json"

# Ensure output directories exist
mkdir -p input/vcf input/plink output

STEP_TIME=$(date +%s)
log "Filtering VCF (removing variants with missing ID) and sex chromosomes..."
bcftools view -e 'ID=="."' -t '^chrX,chrY,X,Y' -m2 -M2 "$INPUT_VCF" -o "$FILTERED_VCF"
log "VCF filtered in $(( $(date +%s) - STEP_TIME )) seconds"

STEP_TIME=$(date +%s)
log "Converting filtered VCF to PLINK format..."
plink2 --vcf "$FILTERED_VCF" --make-bed --out "$PLINK_PREFIX"
log "PLINK files created in $(( $(date +%s) - STEP_TIME )) seconds"

STEP_TIME=$(date +%s)
log "Removing duplicate variants with PLINK..."
plink2 --bfile "$PLINK_PREFIX" --rm-dup force-first --make-bed --out "${PLINK_PREFIX}_dedup"
log "Duplicates removed in $(( $(date +%s) - STEP_TIME )) seconds"

STEP_TIME=$(date +%s)
log "Calculating PRS..."
plink2 --bfile "${PLINK_PREFIX}_dedup" --read-freq ${FREQ_PATH} --score "$PRS_PATH" 1 4 6 header list-variants --out "${PLINK_PREFIX}_dedup.prs"
log "PRS calculated in $(( $(date +%s) - STEP_TIME )) seconds"

STEP_TIME=$(date +%s)
log "Parsing PLINK results to JSON..."
python src/parse_plink_res_to_json.py "${PLINK_PREFIX}_dedup.prs.sscore" > "$OUTPUT_JSON"
log "JSON created in $(( $(date +%s) - STEP_TIME )) seconds"

if [ "$CLEAN_TMP_FILES" = "true" ]; then
    log "Cleaning up temporary files..."
    rm -f "$FILTERED_VCF"
    rm -f "$PLINK_PREFIX".bed "$PLINK_PREFIX".bim "$PLINK_PREFIX".fam "$PLINK_PREFIX".log "$PLINK_PREFIX".nosex "$PLINK_PREFIX".prs.nopred
    rm -f "${PLINK_PREFIX}_dedup".bed "${PLINK_PREFIX}_dedup".bim "${PLINK_PREFIX}_dedup".fam "${PLINK_PREFIX}_dedup".log "${PLINK_PREFIX}_dedup.prs".log "${PLINK_PREFIX}_dedup.prs".nosex "${PLINK_PREFIX}_dedup.prs".profile "${PLINK_PREFIX}_dedup".prs.sscore "${PLINK_PREFIX}_dedup".prs.sscore.vars
    log "Temporary files removed"
fi

log "Done. JSON output at $OUTPUT_JSON"
log "Total runtime: $(( $(date +%s) - START_TIME )) seconds"