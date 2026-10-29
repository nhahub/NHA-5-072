import math
from src.models.financial import InstallmentSchedule, ROIResult

def validate_installment_consistency(schedule: InstallmentSchedule, tolerance: float = 1.0) -> tuple[bool, str]:
    """
    Validates arithmetic consistency between down payment, installments, and total contracted price.
    """
    calculated_sum = schedule.down_payment + sum(item.amount for item in schedule.schedule)
    difference = abs(calculated_sum - schedule.total_paid)

    if difference > tolerance:
        return False, f"Installment sum ({calculated_sum:.2f}) does not match total paid ({schedule.total_paid:.2f}), diff: {difference:.2f}"

    if schedule.total_paid <= 0:
        return False, "Total paid must be positive."

    return True, "Installment schedule is numerically valid."

def validate_roi_consistency(roi: ROIResult) -> tuple[bool, str]:
    """
    Validates arithmetic bounds and consistency of ROI calculations.
    """
    if roi.purchase_price <= 0:
        return False, "Purchase price must be positive."

    expected_gain = roi.projected_exit_value - roi.purchase_price
    if abs(expected_gain - roi.cumulative_capital_gain) > 1.0:
        return False, f"Capital gain discrepancy: projected - purchase ({expected_gain:.2f}) != recorded ({roi.cumulative_capital_gain:.2f})"

    expected_roi_pct = (roi.total_return_amount / roi.purchase_price) * 100.0
    if abs(expected_roi_pct - roi.total_roi_percentage) > 0.1:
        return False, f"ROI percentage discrepancy: expected {expected_roi_pct:.2f}% vs recorded {roi.total_roi_percentage:.2f}%"

    return True, "ROI calculation is numerically consistent."
