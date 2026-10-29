import math
from typing import Literal
from src.models.financial import InstallmentItem, InstallmentSchedule
from src.models.property import PaymentPlan

def get_periods_per_year(frequency: str) -> int:
    freq_map = {
        "monthly": 12,
        "quarterly": 4,
        "semi_annual": 2,
        "annual": 1,
    }
    return freq_map.get(frequency.lower(), 4)

def calculate_installment_schedule(
    total_price: float,
    down_payment_pct: float,
    duration_years: float,
    installment_frequency: Literal["monthly", "quarterly", "semi_annual", "annual"] = "quarterly",
    interest_rate: float = 0.0,
    property_id: str = "prop_calc",
    plan_name: str = "Standard Installment Plan",
) -> InstallmentSchedule:
    """
    Deterministically computes the complete installment amortization schedule.
    Supports 0% interest (standard real estate off-plan) and fixed annual rate financing.
    """
    if total_price <= 0:
        raise ValueError("Total price must be greater than zero.")
    if not (0.0 <= down_payment_pct <= 100.0):
        raise ValueError("Down payment percentage must be between 0 and 100.")
    if duration_years <= 0:
        raise ValueError("Duration in years must be greater than zero.")

    down_payment = round(total_price * (down_payment_pct / 100.0), 2)
    financed_amount = round(total_price - down_payment, 2)

    periods_per_year = get_periods_per_year(installment_frequency)
    months_per_period = 12 // periods_per_year
    total_installments = max(1, int(round(duration_years * periods_per_year)))

    if financed_amount <= 0:
        # 100% cash / down payment
        return InstallmentSchedule(
            property_id=property_id,
            plan_name=plan_name,
            total_price=total_price,
            down_payment=down_payment,
            installment_amount=0.0,
            installment_frequency=installment_frequency,
            number_of_installments=0,
            duration_years=duration_years,
            schedule=[],
            total_paid=down_payment,
            effective_annual_rate=0.0,
        )

    if interest_rate <= 0.0:
        # Standard interest-free off-plan developer installment plan
        base_installment = round(financed_amount / total_installments, 2)
        schedule: list[InstallmentItem] = []
        cumulative = down_payment

        for i in range(1, total_installments + 1):
            if i == total_installments:
                # Adjust rounding on last installment
                amount = round(total_price - cumulative, 2)
            else:
                amount = base_installment
            cumulative = round(cumulative + amount, 2)
            remaining = max(0.0, round(total_price - cumulative, 2))

            schedule.append(
                InstallmentItem(
                    period_number=i,
                    due_month=i * months_per_period,
                    amount=amount,
                    cumulative_paid=cumulative,
                    remaining_balance=remaining,
                )
            )

        return InstallmentSchedule(
            property_id=property_id,
            plan_name=plan_name,
            total_price=total_price,
            down_payment=down_payment,
            installment_amount=base_installment,
            installment_frequency=installment_frequency,
            number_of_installments=total_installments,
            duration_years=duration_years,
            schedule=schedule,
            total_paid=round(down_payment + sum(item.amount for item in schedule), 2),
            effective_annual_rate=0.0,
        )
    else:
        # Financed plan with interest rate per period
        periodic_rate = interest_rate / periods_per_year
        # PMT formula: P * (r * (1 + r)^n) / ((1 + r)^n - 1)
        factor = math.pow(1 + periodic_rate, total_installments)
        pmt = round(financed_amount * (periodic_rate * factor) / (factor - 1), 2)

        schedule: list[InstallmentItem] = []
        balance = financed_amount
        cumulative = down_payment

        for i in range(1, total_installments + 1):
            interest_charge = round(balance * periodic_rate, 2)
            principal_charge = round(pmt - interest_charge, 2)
            balance = max(0.0, round(balance - principal_charge, 2))
            cumulative = round(cumulative + pmt, 2)

            schedule.append(
                InstallmentItem(
                    period_number=i,
                    due_month=i * months_per_period,
                    amount=pmt,
                    cumulative_paid=cumulative,
                    remaining_balance=balance,
                )
            )

        total_paid = round(down_payment + sum(item.amount for item in schedule), 2)
        return InstallmentSchedule(
            property_id=property_id,
            plan_name=plan_name,
            total_price=total_price,
            down_payment=down_payment,
            installment_amount=pmt,
            installment_frequency=installment_frequency,
            number_of_installments=total_installments,
            duration_years=duration_years,
            schedule=schedule,
            total_paid=total_paid,
            effective_annual_rate=interest_rate,
        )

def schedule_from_payment_plan(plan: PaymentPlan, property_id: str) -> InstallmentSchedule:
    """Helper to convert a Property's PaymentPlan directly into a calculated schedule."""
    return calculate_installment_schedule(
        total_price=plan.total_price,
        down_payment_pct=plan.down_payment_percentage,
        duration_years=plan.duration_years,
        installment_frequency=plan.installment_frequency,
        interest_rate=plan.interest_rate or 0.0,
        property_id=property_id,
        plan_name=plan.plan_name,
    )
