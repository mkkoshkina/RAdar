import os
import json
import subprocess
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify
from utils import run_plink_pipeline

app = Flask(__name__)

def log_message(msg, log_file=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    if log_file:
        with open(log_file, 'a') as f:
            f.write(log_msg + '\n')
            
def run_plink_prediction(vcf_path, assembly='GRCh37', clean_tmp=True):

    try:
        result = run_plink_pipeline(vcf_path, assembly, clean_tmp)
        
        sample = os.path.basename(vcf_path).replace('.vcf', '')
        
        return {
            "status": "success",
            "results": result,
            "sample_name": sample
        }
        
    except Exception as e:
        error_msg = f"Prediction failed: {str(e)}"
        print(f"[ERROR] {error_msg}")
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
        "assembly": "GRCh37",  // optional, defaults to GRCh37
        "clean_tmp": true  // optional, defaults to true
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        vcf_file = data.get('vcf_file')
        assembly = data.get('assembly', 'GRCh37')  # Default to GRCh37
        clean_tmp = data.get('clean_tmp', True)
        
        if not vcf_file:
            return jsonify({"error": "vcf_file is required"}), 400
        
        # Handle both absolute and relative paths
        if vcf_file.startswith('/'):
            vcf_path = vcf_file
        else:
            vcf_path = vcf_file  # The utils function will handle path resolution
        
        # Validate that the VCF file exists (if using mounted volume approach)
        if not os.path.exists(vcf_path) and not vcf_file.startswith('input/'):
            # Try with input/ prefix
            vcf_path = os.path.join('input', vcf_file)
            if not os.path.exists(vcf_path):
                return jsonify({"error": f"VCF file not found: {vcf_file}"}), 404
        
        result = run_plink_prediction(vcf_path, assembly, clean_tmp)
        
        if result["status"] == "error":
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting PLINK Prediction API...")
    app.run(host='0.0.0.0', port=5000, debug=False)
