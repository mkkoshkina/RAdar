import json
import sys

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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_plink_res_to_json.py <input_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    result = parse_profile_file(input_file)
    print(json.dumps(result, indent=2))