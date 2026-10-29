from typing import Any, Literal
from pydantic import BaseModel, Field

InvestmentGoal = Literal["capital_growth", "rental_yield", "personal_use", "balanced"]
RiskTolerance = Literal["conservative", "moderate", "aggressive"]

class UserPreferences(BaseModel):
    """Extracted or configured user preferences."""
    budget_max: float | None = None
    budget_min: float | None = None
    currency: str = "EGP"
    preferred_locations: list[str] = Field(default_factory=list)
    preferred_property_types: list[str] = Field(default_factory=list)
    min_bedrooms: int | None = None
    max_down_payment_pct: float | None = None
    min_installment_years: float | None = None
    investment_goal: InvestmentGoal = "balanced"
    risk_tolerance: RiskTolerance = "moderate"
    holding_period_years: int = 5

class ResearchTask(BaseModel):
    """A granular, dependency-aware research task produced by the Planner."""
    task_id: str = Field(description="Unique task identifier, e.g. T01")
    description: str = Field(description="Specific research action or inquiry")
    priority: int = Field(default=1, ge=1, le=6, description="1 is highest priority")
    task_type: Literal[
        "property_search",
        "property_details",
        "developer_research",
        "financial_analysis",
        "market_research",
        "comparison",
        "scenario_analysis",
        "general_research"
    ]
    dependencies: list[str] = Field(default_factory=list, description="List of task_ids required before this task")
    required_tools: list[str] = Field(default_factory=list)
    completion_criteria: str = Field(description="Concrete condition to consider task resolved")
    status: Literal["pending", "in_progress", "completed", "failed", "insufficient_data"] = "pending"
    result_summary: str | None = None

class ResearchPlan(BaseModel):
    """The structured research decomposition output by the Planner."""
    plan_id: str
    original_query: str
    interpreted_intent: str
    constraints_extracted: dict[str, Any] = Field(default_factory=dict)
    tasks: list[ResearchTask] = Field(default_factory=list)
    execution_order: list[str] = Field(default_factory=list, description="Topologically sorted task_ids")
    estimated_complexity: Literal["simple", "moderate", "complex"] = "moderate"

__all__ = [
    "InvestmentGoal",
    "RiskTolerance",
    "UserPreferences",
    "ResearchTask",
    "ResearchPlan",
]

