# RAdar documentation

This repository contains two main components:
1. **A service platform**
2. **RA Polygenic Risk Score Pipeline** - A pipeline for processing VCF files and calculating polygenic risk scores

## How to Use the PLINK API
#### Health Check

Check if the service is running:

```bash
curl http://localhost:5000/health
```

#### Predict Endpoint

Submit a POST request to `/predict` with a JSON payload specifying your VCF file and (optionally) whether to clean temporary files.

**Example using `curl`:**

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "vcf_file": "input/vcf/sample.vcf",
    "clean_tmp": true
  }'
```

- `vcf_file`: Path to your VCF file, relative to the `/input` directory inside the container (e.g., `vcf/sample.vcf`).
- `clean_tmp`: (Optional) Boolean, whether to clean up temporary files after processing (default: `true`).

**Note:**  
The assembly is currently set to `'GRCh37'` by default in the API code. `'GRCh38'` is in progress.

### Output

- The API will return a JSON response with the results or an error message.

```
{"log_file":"log/lm5515.log","output_json":"output/lm5515.json","status":"success","table_snps_used":"output/final_prs_table.tsv"}
```
