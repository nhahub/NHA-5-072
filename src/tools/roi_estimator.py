from pydantic import BaseModel, Field
from src.tools.base import BaseTool, ToolResult
from src.engine.roi import estimate_roi
from src.models.evidence import EvidenceRecord

class ROIEstimatorParams(BaseModel):
    purchase_price: float = Field(gt=0, description="Purchase price of unit in EGP")
    holding_period_years: int = Field(default=5, ge=1, le=20, description="Investment horizon in years")
    annual_appreciation_rate: float = Field(
        default=0.12, ge=0.0, le=0.50, description="Projected annual capital appreciation (e.g. 0.12 for 12%)"
    )
    annual_rental_yield_rate: float | None = Field(
        default=0.07, ge=0.0, le=0.30, description="Gross rental yield percentage (e.g. 0.07 for 7%)"
    )
    property_id: str = Field(default="CALC_001", description="Associated Property ID")

class ROIEstimatorTool(BaseTool):
    name = "ROIEstimatorTool"
    description = "Estimates capital gain, cumulative rental income, and net return on investment (ROI) deterministically."
    parameters_schema = ROIEstimatorParams

    def execute(self, params: ROIEstimatorParams) -> ToolResult:
        res = estimate_roi(
            purchase_price=params.purchase_price,
            holding_period_years=params.holding_period_years,
            annual_appreciation_rate=params.annual_appreciation_rate,
            annual_rental_yield_rate=params.annual_rental_yield_rate,
            property_id=params.property_id,
        )

        content = (
            f"ROI Projection for Property {params.property_id} ({params.holding_period_years}-Year Horizon): "
            f"Base Purchase Price: {res.purchase_price:,.0f} EGP. "
            f"Projected Exit Value: {res.projected_exit_value:,.0f} EGP (Gain: +{res.cumulative_capital_gain:,.0f} EGP). "
            f"Cumulative Net Rental Income: {res.cumulative_rental_income:,.0f} EGP. "
            f"Total Return: {res.total_return_amount:,.0f} EGP ({res.total_roi_percentage:.1f}% Total ROI). "
            f"Assumptions: {'; '.join(res.assumptions)}."
        )

        evidence = [
            EvidenceRecord(
                evidence_id=f"E-CALC-ROI-{params.property_id}",
                task_id="T_FIN_ROI",
                source_type="financial_calculation",
                source_reference="ROIEngine.estimate_roi",
                retrieval_method="compound_financial_formula",
                content=content,
                metadata=res.model_dump(),
            )
        ]

        return ToolResult(
            success=True,
            data=res.model_dump(),
            evidence_records=evidence,
        )
