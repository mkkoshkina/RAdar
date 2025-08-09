from flask import Flask, request, jsonify
from utils import run_plink_pipeline

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "plink-predictor"})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    vcf_file = data.get('vcf_file')
    # assembly = data.get('assembly')
    assembly='GRCh37'
    clean_tmp = data.get('clean_tmp')
    if not vcf_file or not assembly:
        return jsonify({"error": "vcf_file and assembly are required"}), 400
    try:
        result = run_plink_pipeline(vcf_file, assembly, clean_tmp)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting PLINK Prediction API...")
    app.run(host='0.0.0.0', port=5000, debug=False)