from typing import Literal
from pydantic import BaseModel, Field

class InstallmentItem(BaseModel):
    """A scheduled installment event."""
    period_number: int
    due_month: int
    amount: float
    cumulative_paid: float
    remaining_balance: float

class InstallmentSchedule(BaseModel):
    """Complete installment schedule breakdown."""
    property_id: str
    plan_name: str
    total_price: float
    down_payment: float
    installment_amount: float
    installment_frequency: str
    number_of_installments: int
    duration_years: float
    schedule: list[InstallmentItem] = Field(default_factory=list)
    total_paid: float
    effective_annual_rate: float | None = 0.0

class ROIResult(BaseModel):
    """Estimated return on investment and projections."""
    property_id: str
    purchase_price: float
    holding_period_years: int
    annual_appreciation_rate: float
    projected_exit_value: float
    cumulative_capital_gain: float
    annual_rental_yield_rate: float | None = None
    cumulative_rental_income: float | None = None
    net_operating_expenses: float | None = None
    total_return_amount: float
    total_roi_percentage: float
    assumptions: list[str] = Field(default_factory=list)
    confidence_level: Literal["low", "medium", "high"] = "medium"
    evidence_ids: list[str] = Field(default_factory=list)

class ScenarioResult(BaseModel):
    """Outcome for a specific investment scenario."""
    scenario_name: str
    description: str
    parameters_changed: dict[str, float | str]
    financial_outcome: ROIResult
    comparison_to_base_delta_pct: float

class FinancialAnalysis(BaseModel):
    """Aggregated financial results for a property."""
    property_id: str
    selected_payment_plan: InstallmentSchedule
    baseline_roi: ROIResult
    scenarios: list[ScenarioResult] = Field(default_factory=list)
    summary_notes: str | None = None
