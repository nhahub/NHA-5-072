from typing import Any
from src.models.financial import ScenarioResult, ROIResult
from src.engine.roi import estimate_roi

def run_scenario_analysis(
    purchase_price: float,
    baseline_roi: ROIResult,
    custom_scenarios: list[dict[str, Any]] | None = None,
) -> list[ScenarioResult]:
    """
    Evaluates sensitivity scenarios (e.g., Bearish, Moderate, Bullish market conditions).
    """
    scenarios_to_run = custom_scenarios or [
        {
            "name": "Conservative Market",
            "description": "Lower appreciation rate and modest rental yields.",
            "appreciation_rate": max(0.04, baseline_roi.annual_appreciation_rate - 0.05),
            "rental_yield": max(0.04, (baseline_roi.annual_rental_yield_rate or 0.06) - 0.02),
        },
        {
            "name": "Base Market Case",
            "description": "Expected steady market appreciation and occupancy.",
            "appreciation_rate": baseline_roi.annual_appreciation_rate,
            "rental_yield": baseline_roi.annual_rental_yield_rate or 0.07,
        },
        {
            "name": "High-Growth Prime Case",
            "description": "Premium infrastructure delivery and accelerated capital appreciation.",
            "appreciation_rate": baseline_roi.annual_appreciation_rate + 0.06,
            "rental_yield": (baseline_roi.annual_rental_yield_rate or 0.07) + 0.02,
        },
    ]

    results: list[ScenarioResult] = []

    for sc in scenarios_to_run:
        app_rate = float(sc.get("appreciation_rate", baseline_roi.annual_appreciation_rate))
        rent_rate = float(sc.get("rental_yield", baseline_roi.annual_rental_yield_rate or 0.07))
        holding_years = int(sc.get("holding_years", baseline_roi.holding_period_years))

        outcome = estimate_roi(
            purchase_price=purchase_price,
            holding_period_years=holding_years,
            annual_appreciation_rate=app_rate,
            annual_rental_yield_rate=rent_rate,
            property_id=baseline_roi.property_id,
        )

        delta_pct = round(outcome.total_roi_percentage - baseline_roi.total_roi_percentage, 2)

        results.append(
            ScenarioResult(
                scenario_name=sc["name"],
                description=sc["description"],
                parameters_changed={
                    "annual_appreciation_rate": f"{app_rate * 100:.1f}%",
                    "annual_rental_yield_rate": f"{rent_rate * 100:.1f}%",
                    "holding_period_years": holding_years,
                },
                financial_outcome=outcome,
                comparison_to_base_delta_pct=delta_pct,
            )
        )

    return results
