from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, UploadFile, Form
import requests
import os

from backend.core.container import Container
from backend.core.dependencies import get_current_user_payload
from backend.core.exceptions import PredictionError, ValidationError
from backend.schema.auth_schema import Payload
from backend.schema.genetic_analysis_schema import GeneticAnalysisResponse, GeneticAnalysisCost
from backend.services.billing_service import BillingService
from backend.utils.date import get_now

router = APIRouter(
    prefix="/genetic-analysis",
    tags=["genetic-analysis"],
)

GENETIC_ANALYSIS_COST = 50

@router.post("/analyze-rheumatoid-arthritis", response_model=GeneticAnalysisResponse)
@inject
async def analyze_rheumatoid_arthritis_risk(
        vcf_file: UploadFile = File(...),
        current_user_payload: Payload = Depends(get_current_user_payload),
        billing_service: BillingService = Depends(Provide[Container.billing_service])
):
    if not billing_service.reserve_funds(current_user_payload.id, GENETIC_ANALYSIS_COST):
        raise PredictionError(detail=f"Insufficient funds for genetic analysis. Required: {GENETIC_ANALYSIS_COST} credits.")

    try:
        vcf_dir = 'input/vcf'
        os.makedirs(vcf_dir, exist_ok=True)
        vcf_path = os.path.join(vcf_dir, vcf_file.filename)
        
        with open(vcf_path, 'wb') as f:
            content = await vcf_file.read()
            f.write(content)
        
        plink_api_url = os.environ.get("PLINK_API_URL", "http://plink:5000")
        payload = {
            "vcf_file": f"vcf/{vcf_file.filename}",
            "prs_file": "prs/PGS002769_hmPOS_GRCh38.txt"
        }
        
        response = requests.post(f"{plink_api_url}/predict", json=payload, timeout=300)
        response.raise_for_status()
        plink_result = response.json()
        
        transaction = billing_service.finalize_transaction(current_user_payload.id, GENETIC_ANALYSIS_COST)
        
        try:
            os.remove(vcf_path)
        except:
            pass  
        
        return GeneticAnalysisResponse(
            status="success",
            analysis_result=plink_result,
            transaction_id=transaction.id,
            cost=GENETIC_ANALYSIS_COST,
            timestamp=get_now()
        )
        
    except requests.RequestException as e:
        billing_service.cancel_reservation(current_user_payload.id, GENETIC_ANALYSIS_COST)
        raise PredictionError(detail=f"Analysis service error: {str(e)}")
    except Exception as e:
        billing_service.cancel_reservation(current_user_payload.id, GENETIC_ANALYSIS_COST)
        try:
            if 'vcf_path' in locals():
                os.remove(vcf_path)
        except:
            pass
        raise PredictionError(detail=f"An error occurred during analysis: {str(e)}")


@router.get("/cost", response_model=GeneticAnalysisCost)
async def get_analysis_cost():
    return GeneticAnalysisCost(cost=GENETIC_ANALYSIS_COST)
