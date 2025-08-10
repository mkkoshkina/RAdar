import os
import base64

import requests

API_URL = os.environ.get("API_URL", "http://localhost:8000/api")
PLINK_API_URL = os.environ.get("PLINK_API_URL", "http://plink:5000")


class APIClient:
    def __init__(self, base_url=API_URL):
        self.base_url = base_url

    def _send_request(self, method, path, token=None, **kwargs):
        headers = kwargs.get('headers', {})
        if token:
            headers['Authorization'] = f'Bearer {token}'
        response = requests.request(method, f"{self.base_url}{path}", headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def get(self, path, token=None, **kwargs):
        return self._send_request('GET', path, token=token, **kwargs)

    def post(self, path, token=None, **kwargs):
        return self._send_request('POST', path, token=token, **kwargs)


api_client = APIClient()


def fetch_users_report(user_session):
    return api_client.get("/v1/admin/users-report", token=user_session['access_token'])


def fetch_predictions_reports(user_session):
    return api_client.get("/v1/admin/predictions-reports", token=user_session['access_token'])


def fetch_credits_report(user_session):
    return api_client.get("/v1/admin/credits-report", token=user_session['access_token'])


def fetch_user_balance(user_session):
    response = api_client.get("/v1/billing/balance", token=user_session['access_token'])
    return response


def deposit_amount(amount, user_session):
    response = api_client.post("/v1/billing/deposit", token=user_session['access_token'], json={"amount": amount})
    return response


def fetch_transaction_history(user_session):
    response = api_client.get("/v1/billing/history", token=user_session['access_token'])
    return response


def fetch_models(user_session):
    response = api_client.get("/v1/prediction/models", token=user_session['access_token'])
    return response


def fetch_prediction_history(user_session):
    response = api_client.get("/v1/prediction/history", token=user_session['access_token'])
    return response


def send_prediction_request(selected_model, merchant_ids, cluster_ids, user_session):
    payload = {
        "model_name": selected_model,
        "features": [{"merchant_id": m_id, "cluster_id": c_id} for m_id, c_id in zip(merchant_ids, cluster_ids)]
    }
    response = api_client.post("/v1/prediction/make", json=payload, token=user_session['access_token'])
    return response


def authenticate_user(email, password):
    try:
        response = api_client.post("/v1/auth/sign-in", json={"email": email, "password": password})
        if response:
            return response, None
        else:
            return None, "Authentification failed: No response from server"
    except Exception as e:
        return None, str(e)


def register_user(email, password, name):
    try:
        response = api_client.post("/v1/auth/sign-up", json={"email": email, "password": password, "name": name})
        if response:
            return response, None
        else:
            return None, "Registration failed: No response from server"
    except Exception as e:
        return None, str(e)


def call_plink_prediction(vcf_filename):
    try:
        payload = {
            "vcf_file": f"vcf/{vcf_filename}",
            "prs_file": "prs/PGS002769_hmPOS_GRCh38.txt"
        }
        response = requests.post(f"{PLINK_API_URL}/predict", json=payload, timeout=300)
        response.raise_for_status()
        return response.json(), None
    except Exception as e:
        return None, str(e)


def analyze_rheumatoid_arthritis_risk(vcf_file_content, filename, user_session):
    try:
        files = {
            'vcf_file': (filename, vcf_file_content, 'text/plain')
        }
        
        response = requests.post(
            f"{API_URL}/v1/genetic-analysis/analyze-rheumatoid-arthritis",
            files=files,
            headers={'Authorization': f'Bearer {user_session["access_token"]}'},
            timeout=300
        )
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") == "success" and "analysis_result" in result:
            return result["analysis_result"], None
        else:
            return None, "Analysis failed: No valid result returned"
            
    except requests.HTTPError as e:
        if e.response.status_code == 422:  # Validation error
            error_detail = e.response.json().get('detail', 'Validation error')
            return None, error_detail
        else:
            return None, f"HTTP error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


def get_genetic_analysis_cost():
    try:
        response = api_client.get("/v1/genetic-analysis/cost")
        return response.get("cost", 50)  
    except:
        return 50  


import os
import base64
import requests

API_URL = os.environ.get("API_URL", "http://localhost:8000/api")
PLINK_API_URL = os.environ.get("PLINK_API_URL", "http://plink:5000")


class APIClient:
    def __init__(self, base_url=API_URL):
        self.base_url = base_url

    def _send_request(self, method, path, token=None, timeout=300, **kwargs):  # 5 minute default timeout
        headers = kwargs.get('headers', {})
        if token:
            headers['Authorization'] = f'Bearer {token}'
        response = requests.request(
            method, 
            f"{self.base_url}{path}", 
            headers=headers, 
            timeout=timeout,  # Add timeout parameter
            **kwargs
        )
        response.raise_for_status()
        return response.json()

    def get(self, path, token=None, timeout=300, **kwargs):
        return self._send_request('GET', path, token=token, timeout=timeout, **kwargs)

    def post(self, path, token=None, timeout=300, **kwargs):
        return self._send_request('POST', path, token=token, timeout=timeout, **kwargs)

api_client = APIClient()

def send_chat_message(message, session_id):
    client = APIClient()
    response = client.post('/v1/chatbot/chat', 
                          json={'message': message, 'session_id': session_id},
                          timeout=300)  # 5 minutes timeout
    if response and 'response' in response:
        return response['response']
    return "No response from server."