from typing import Literal
from pydantic import BaseModel, Field

class PaymentPlan(BaseModel):
    """Structured installment or payment plan."""
    plan_name: str = Field(description="Name or title of payment plan")
    total_price: float = Field(description="Total contracted price in specified currency")
    currency: str = Field(default="EGP")
    down_payment_percentage: float = Field(ge=0.0, le=100.0)
    down_payment_amount: float = Field(ge=0.0)
    number_of_installments: int = Field(ge=1)
    installment_amount: float = Field(ge=0.0)
    installment_frequency: Literal["monthly", "quarterly", "semi_annual", "annual"] = "quarterly"
    duration_years: float = Field(ge=0.1)
    interest_rate: float | None = Field(default=0.0, ge=0.0, description="Annual interest rate, 0 for interest-free")
    maintenance_deposit: float | None = Field(default=0.0)
    club_membership: float | None = Field(default=0.0)
    notes: str | None = None

class PropertyListing(BaseModel):
    """A real-estate property listing with verified attributes."""
    property_id: str
    project_name: str
    developer_name: str
    property_type: Literal[
        "apartment",
        "villa",
        "townhouse",
        "duplex",
        "penthouse",
        "studio",
        "chalet",
        "office",
        "retail",
        "land"
    ]
    location: str
    sub_location: str | None = None
    area_sqm: float = Field(gt=0.0)
    bedrooms: int | None = Field(default=None, ge=0)
    bathrooms: int | None = Field(default=None, ge=0)
    floor: int | None = None
    finishing: Literal["finished", "semi_finished", "core_and_shell"] | None = None
    delivery_date: str | None = None
    price: float = Field(gt=0.0)
    price_per_sqm: float = Field(gt=0.0)
    payment_plans: list[PaymentPlan] = Field(default_factory=list)
    amenities: list[str] = Field(default_factory=list)
    description: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)

class Developer(BaseModel):
    """Developer profile and track record."""
    developer_id: str
    name: str
    established_year: int | None = None
    headquarters: str | None = None
    notable_projects: list[str] = Field(default_factory=list)
    total_delivered_units: int | None = None
    reputation_notes: str | None = None
    financial_solvency_rating: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)

class PropertyFilter(BaseModel):
    """Query filters for property search."""
    location: str | None = None
    sub_location: str | None = None
    property_type: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    min_area_sqm: float | None = None
    max_area_sqm: float | None = None
    bedrooms: int | None = None
    developer_name: str | None = None
    finishing: str | None = None
    delivery_year: int | None = None
    max_down_payment: float | None = None
    min_duration_years: float | None = None
