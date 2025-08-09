import os
import json
import subprocess
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify
from parse_plink_res_to_json import parse_profile_file

app = Flask(__name__)

def log_message(msg, log_file=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    if log_file:
        with open(log_file, 'a') as f:
            f.write(log_msg + '\n')

def run_plink_prediction(vcf_path, prs_path, clean_tmp=True):
    try:
        sample = os.path.basename(vcf_path).replace('.hg38.vcf', '')
        
        log_dir = "log"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{sample}.log")
        
        start_time = datetime.now()
        log_message("Starting PLINK prediction", log_file)
        log_message(f"Input VCF: {vcf_path}", log_file)
        log_message(f"PRS file: {prs_path}", log_file)
        
        filtered_vcf = f"input/vcf/{sample}.hg38.filtered.vcf"
        plink_prefix = f"input/plink/{sample}"
        
        os.makedirs("input/vcf", exist_ok=True)
        os.makedirs("input/plink", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        
        log_message("Filtering VCF (removing variants with missing ID)...", log_file)
        step_start = datetime.now()
        result = subprocess.run([
            'bcftools', 'filter', '-e', 'ID=="."', vcf_path, '-o', filtered_vcf
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"BCFtools filtering failed: {result.stderr}")
        
        step_duration = (datetime.now() - step_start).total_seconds()
        log_message(f"VCF filtered in {step_duration:.1f} seconds", log_file)
        
        log_message("Converting filtered VCF to PLINK format...", log_file)
        step_start = datetime.now()
        result = subprocess.run([
            'plink', '--vcf', filtered_vcf, '--make-bed', '--out', plink_prefix
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"PLINK conversion failed: {result.stderr}")
        
        step_duration = (datetime.now() - step_start).total_seconds()
        log_message(f"PLINK files created in {step_duration:.1f} seconds", log_file)
        
        log_message("Calculating PRS...", log_file)
        step_start = datetime.now()
        result = subprocess.run([
            'plink', '--bfile', plink_prefix, '--score', prs_path, '1', '4', '6', 'header', '--out', f"{plink_prefix}.prs"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"PLINK PRS calculation failed: {result.stderr}")
        
        step_duration = (datetime.now() - step_start).total_seconds()
        log_message(f"PRS calculated in {step_duration:.1f} seconds", log_file)
        
        log_message("Parsing PLINK results to JSON...", log_file)
        step_start = datetime.now()
        profile_file = f"{plink_prefix}.prs.profile"
        
        if not os.path.exists(profile_file):
            raise Exception(f"Profile file not found: {profile_file}")
        
        results = parse_profile_file(profile_file)
        step_duration = (datetime.now() - step_start).total_seconds()
        log_message(f"JSON created in {step_duration:.1f} seconds", log_file)
        
        if clean_tmp:
            log_message("Cleaning up temporary files...", log_file)
            temp_files = [
                filtered_vcf,
                f"{plink_prefix}.bed", f"{plink_prefix}.bim", f"{plink_prefix}.fam",
                f"{plink_prefix}.log", f"{plink_prefix}.nosex", f"{plink_prefix}.prs.nopred",
                f"{plink_prefix}.prs.log", f"{plink_prefix}.prs.nosex", f"{plink_prefix}.prs.profile"
            ]
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            log_message("Temporary files removed", log_file)
        
        total_duration = (datetime.now() - start_time).total_seconds()
        log_message(f"Prediction completed in {total_duration:.1f} seconds", log_file)
        
        return {
            "status": "success",
            "results": results,
            "sample_name": sample,
            "duration": total_duration
        }
        
    except Exception as e:
        error_msg = f"Prediction failed: {str(e)}"
        log_message(error_msg, log_file if 'log_file' in locals() else None)
        return {
            "status": "error",
            "error": error_msg
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "plink-predictor"})

@app.route('/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint
    Expected JSON payload:
    {
        "vcf_file": "relative/path/to/file.vcf",
        "prs_file": "relative/path/to/prs.txt",
        "clean_temp": true  // optional, defaults to true
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        vcf_file = data.get('vcf_file')
        prs_file = data.get('prs_file')
        clean_temp = data.get('clean_temp', True)
        
        if not vcf_file or not prs_file:
            return jsonify({"error": "Both vcf_file and prs_file are required"}), 400
        
        vcf_path = os.path.join('/input', vcf_file)
        prs_path = os.path.join('/input', prs_file)
        
        if not os.path.exists(vcf_path):
            return jsonify({"error": f"VCF file not found: {vcf_path}"}), 404
        
        if not os.path.exists(prs_path):
            return jsonify({"error": f"PRS file not found: {prs_path}"}), 404
        
        result = run_plink_prediction(vcf_path, prs_path, clean_temp)
        
        if result["status"] == "error":
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting PLINK Prediction API...")
    app.run(host='0.0.0.0', port=5000, debug=False)