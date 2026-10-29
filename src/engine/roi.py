from typing import Literal
from src.models.financial import ROIResult

def estimate_roi(
    purchase_price: float,
    holding_period_years: int = 5,
    annual_appreciation_rate: float = 0.12,  # e.g., 12% annual appreciation
    annual_rental_yield_rate: float | None = 0.07,  # e.g., 7% gross rental yield
    annual_operating_expense_rate: float = 0.015,  # 1.5% maintenance / property tax / vacancy
    property_id: str = "prop_calc",
    evidence_ids: list[str] | None = None,
) -> ROIResult:
    """
    Deterministically computes capital appreciation, rental yield, and net ROI over a holding period.
    """
    if purchase_price <= 0:
        raise ValueError("Purchase price must be positive.")
    if holding_period_years <= 0:
        raise ValueError("Holding period must be at least 1 year.")

    # Future property value under compound appreciation
    projected_exit_value = round(purchase_price * ((1.0 + annual_appreciation_rate) ** holding_period_years), 2)
    cumulative_capital_gain = round(projected_exit_value - purchase_price, 2)

    assumptions = [
        f"Annual capital appreciation estimated at {annual_appreciation_rate * 100:.1f}%.",
        f"Holding period set to {holding_period_years} years.",
    ]

    cumulative_rental_income: float | None = None
    net_operating_expenses: float | None = None

    if annual_rental_yield_rate and annual_rental_yield_rate > 0:
        # Net rental yield per year
        effective_yield = max(0.0, annual_rental_yield_rate - annual_operating_expense_rate)
        # Assuming rent scales with property value average or baseline
        # For conservative institutional estimation, annual rental income is computed based on starting price escalated moderately
        gross_rent_annual = purchase_price * annual_rental_yield_rate
        net_rent_annual = purchase_price * effective_yield

        cumulative_rental_income = round(net_rent_annual * holding_period_years, 2)
        net_operating_expenses = round((purchase_price * annual_operating_expense_rate) * holding_period_years, 2)
        total_return_amount = round(cumulative_capital_gain + cumulative_rental_income, 2)
        assumptions.append(f"Gross rental yield estimated at {annual_rental_yield_rate * 100:.1f}%.")
        assumptions.append(f"Operating & vacancy expense allowance estimated at {annual_operating_expense_rate * 100:.1f}% annually.")
    else:
        total_return_amount = cumulative_capital_gain
        assumptions.append("Pure capital growth strategy; rental income not factored.")

    total_roi_percentage = round((total_return_amount / purchase_price) * 100.0, 2)

    confidence: Literal["low", "medium", "high"] = "medium"
    if holding_period_years > 7:
        confidence = "low"
    elif holding_period_years <= 3 and annual_appreciation_rate <= 0.15:
        confidence = "high"

    return ROIResult(
        property_id=property_id,
        purchase_price=purchase_price,
        holding_period_years=holding_period_years,
        annual_appreciation_rate=annual_appreciation_rate,
        projected_exit_value=projected_exit_value,
        cumulative_capital_gain=cumulative_capital_gain,
        annual_rental_yield_rate=annual_rental_yield_rate,
        cumulative_rental_income=cumulative_rental_income,
        net_operating_expenses=net_operating_expenses,
        total_return_amount=total_return_amount,
        total_roi_percentage=total_roi_percentage,
        assumptions=assumptions,
        confidence_level=confidence,
        evidence_ids=evidence_ids or [],
    )
