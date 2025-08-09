#!/bin/bash

INPUT_VCF=$1      # e.g., input/vcf/ng1657.hg38.vcf
PRS_PATH=$2       # e.g., input/prs/PGS002769_hmPOS_GRCh38.txt
CLEAN_TMP_FILES=${3:-true}  # true/false, default to false

# Extract sample name (basename without .hg38.vcf)
sample=$(basename "$INPUT_VCF" .hg38.vcf)

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
FILTERED_VCF="input/vcf/${sample}.hg38.filtered.vcf"
PLINK_PREFIX="input/plink/${sample}"
OUTPUT_JSON="output/${sample}.json"

# Ensure output directories exist
mkdir -p input/vcf input/plink output

STEP_TIME=$(date +%s)
log "Filtering VCF (removing variants with missing ID)..."
bcftools filter -e 'ID=="."' "$INPUT_VCF" -o "$FILTERED_VCF"
log "VCF filtered in $(( $(date +%s) - STEP_TIME )) seconds"

STEP_TIME=$(date +%s)
log "Converting filtered VCF to PLINK format..."
plink --vcf "$FILTERED_VCF" --make-bed --out "$PLINK_PREFIX"
log "PLINK files created in $(( $(date +%s) - STEP_TIME )) seconds"

STEP_TIME=$(date +%s)
log "Calculating PRS..."
plink --bfile "$PLINK_PREFIX" --score "$PRS_PATH" 1 4 6 header --out "$PLINK_PREFIX.prs"
log "PRS calculated in $(( $(date +%s) - STEP_TIME )) seconds"

STEP_TIME=$(date +%s)
log "Parsing PLINK results to JSON..."
python src/parse_plink_res_to_json.py "$PLINK_PREFIX.prs.profile" > "$OUTPUT_JSON"
log "JSON created in $(( $(date +%s) - STEP_TIME )) seconds"

if [ "$CLEAN_TMP_FILES" = "true" ]; then
    log "Cleaning up temporary files..."
    rm -f "$FILTERED_VCF"
    rm -f "$PLINK_PREFIX".bed "$PLINK_PREFIX".bim "$PLINK_PREFIX".fam "$PLINK_PREFIX".log "$PLINK_PREFIX".nosex "$PLINK_PREFIX".prs.nopred
    rm -f "$PLINK_PREFIX.prs".log "$PLINK_PREFIX.prs".nosex "$PLINK_PREFIX.prs".profile
    log "Temporary files removed"
fi

log "Done. JSON output at $OUTPUT_JSON"
log "Total runtime: $(( $(date +%s) - START_TIME )) seconds"