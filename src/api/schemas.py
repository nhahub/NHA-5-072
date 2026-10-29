from typing import Any
from pydantic import BaseModel, Field
from src.models.research import UserPreferences
from src.models.report import FinalReport
from src.models.evidence import EvidenceArsenal
from src.models.property import PropertyListing
from src.models.financial import InstallmentSchedule, ROIResult, ScenarioResult

class ResearchRequest(BaseModel):
    query: str = Field(description="Natural-language investment or property-search request")
    preferences: UserPreferences | None = None
    session_id: str | None = "default_session"

class ResearchResponse(BaseModel):
    research_id: str
    status: str
    final_report: FinalReport | None = None
    evidence_count: int = 0
    trajectory: list[dict[str, Any]] = []

class PropertySearchRequest(BaseModel):
    location: str | None = None
    property_type: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    bedrooms: int | None = None
    developer_name: str | None = None

class InstallmentRequest(BaseModel):
    total_price: float
    down_payment_pct: float = 10.0
    duration_years: float = 7.0
    frequency: str = "quarterly"
    interest_rate: float = 0.0
    property_id: str = "PROP_CALC"

class ROIRequest(BaseModel):
    purchase_price: float
    holding_period_years: int = 5
    annual_appreciation_rate: float = 0.12
    annual_rental_yield_rate: float = 0.07
    property_id: str = "PROP_CALC"
