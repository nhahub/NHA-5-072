from typing import Literal
from pydantic import BaseModel, Field
from src.tools.base import BaseTool, ToolResult
from src.engine.installments import calculate_installment_schedule
from src.models.evidence import EvidenceRecord

class InstallmentCalcParams(BaseModel):
    total_price: float = Field(gt=0, description="Total property price in EGP")
    down_payment_pct: float = Field(ge=0, le=100, default=10.0, description="Down payment percentage (e.g. 10.0 for 10%)")
    duration_years: float = Field(gt=0, default=7.0, description="Installment plan duration in years (e.g. 7.0)")
    frequency: Literal["monthly", "quarterly", "semi_annual", "annual"] = Field(
        default="quarterly", description="Payment frequency"
    )
    interest_rate: float = Field(default=0.0, ge=0.0, description="Annual financing rate, 0.0 for interest-free")
    property_id: str = Field(default="CALC_001", description="Property ID reference")

class InstallmentCalcTool(BaseTool):
    name = "InstallmentCalcTool"
    description = "Deterministically calculates down payments, periodic installment schedules, and cash-flow obligations."
    parameters_schema = InstallmentCalcParams

    def execute(self, params: InstallmentCalcParams) -> ToolResult:
        schedule = calculate_installment_schedule(
            total_price=params.total_price,
            down_payment_pct=params.down_payment_pct,
            duration_years=params.duration_years,
            installment_frequency=params.frequency,
            interest_rate=params.interest_rate,
            property_id=params.property_id,
        )

        content = (
            f"Deterministic Payment Plan for Property {params.property_id}: "
            f"Total Price: {schedule.total_price:,.0f} EGP. "
            f"Down Payment ({params.down_payment_pct}%): {schedule.down_payment:,.0f} EGP. "
            f"Number of Installments: {schedule.number_of_installments} ({schedule.installment_frequency}). "
            f"Installment Amount: {schedule.installment_amount:,.2f} EGP over {schedule.duration_years} years. "
            f"Total Capital Outlay: {schedule.total_paid:,.2f} EGP."
        )

        evidence = [
            EvidenceRecord(
                evidence_id=f"E-CALC-INST-{params.property_id}",
                task_id="T_FIN_INSTALLMENT",
                source_type="financial_calculation",
                source_reference="InstallmentEngine.calculate_schedule",
                retrieval_method="deterministic_formula",
                content=content,
                metadata=schedule.model_dump(),
            )
        ]

        return ToolResult(
            success=True,
            data=schedule.model_dump(),
            evidence_records=evidence,
        )
