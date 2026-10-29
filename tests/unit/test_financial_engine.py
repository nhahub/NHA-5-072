import pytest
from src.engine.installments import calculate_installment_schedule
from src.engine.roi import estimate_roi
from src.engine.scenarios import run_scenario_analysis
from src.engine.validators import validate_installment_consistency, validate_roi_consistency

def test_interest_free_installment_calculation():
    # 10M price, 10% DP (1M), 7 years quarterly (28 installments)
    schedule = calculate_installment_schedule(
        total_price=10_000_000.0,
        down_payment_pct=10.0,
        duration_years=7.0,
        installment_frequency="quarterly",
        interest_rate=0.0,
    )

    assert schedule.down_payment == 1_000_000.0
    assert schedule.number_of_installments == 28
    # Financed: 9M / 28 = 321,428.57
    assert len(schedule.schedule) == 28
    assert abs(schedule.total_paid - 10_000_000.0) < 1.0

    valid, msg = validate_installment_consistency(schedule)
    assert valid, msg

def test_roi_compound_calculation():
    # 10M price, 5 years @ 12% annual appreciation
    # projected exit = 10M * (1.12)^5 = 17,623,416.83
    roi = estimate_roi(
        purchase_price=10_000_000.0,
        holding_period_years=5,
        annual_appreciation_rate=0.12,
        annual_rental_yield_rate=0.07,
        annual_operating_expense_rate=0.015,
    )

    assert roi.projected_exit_value > 17_000_000.0
    assert roi.cumulative_capital_gain > 7_000_000.0
    assert roi.cumulative_rental_income is not None
    assert roi.total_roi_percentage > 70.0

    valid, msg = validate_roi_consistency(roi)
    assert valid, msg

def test_scenario_analysis():
    roi = estimate_roi(
        purchase_price=10_000_000.0,
        holding_period_years=5,
        annual_appreciation_rate=0.12,
    )
    scenarios = run_scenario_analysis(purchase_price=10_000_000.0, baseline_roi=roi)
    assert len(scenarios) == 3
    # Check that conservative has lower ROI than bullish
    roi_conservative = scenarios[0].financial_outcome.total_roi_percentage
    roi_bullish = scenarios[2].financial_outcome.total_roi_percentage
    assert roi_bullish > roi_conservative
