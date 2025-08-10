from datetime import datetime
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from backend.utils.date import get_now


class GeneticAnalysisResponse(BaseModel):
    status: str = Field(..., description="Status of the analysis (success/error)")
    analysis_result: Optional[Dict[str, Any]] = Field(None, description="The PLINK analysis result")
    transaction_id: int = Field(..., description="ID of the billing transaction")
    cost: int = Field(..., description="Cost of the analysis in credits")
    timestamp: datetime = Field(default_factory=get_now, description="Timestamp of the analysis")


class GeneticAnalysisCost(BaseModel):
    cost: int = Field(..., description="Cost of genetic analysis in credits")
