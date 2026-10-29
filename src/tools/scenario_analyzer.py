from typing import Any
from pydantic import BaseModel, Field
from src.tools.base import BaseTool, ToolResult
from src.engine.roi import estimate_roi
from src.engine.scenarios import run_scenario_analysis
from src.models.evidence import EvidenceRecord

class ScenarioAnalyzerParams(BaseModel):
    purchase_price: float = Field(gt=0, description="Purchase price in EGP")
    base_appreciation_rate: float = Field(default=0.12, ge=0.0, le=0.50)
    base_rental_yield: float = Field(default=0.07, ge=0.0, le=0.30)
    holding_period_years: int = Field(default=5, ge=1, le=20)
    property_id: str = Field(default="CALC_001")

class ScenarioAnalyzerTool(BaseTool):
    name = "ScenarioAnalyzerTool"
    description = "Executes comparative multi-scenario sensitivity analysis across conservative, base, and aggressive cases."
    parameters_schema = ScenarioAnalyzerParams

    def execute(self, params: ScenarioAnalyzerParams) -> ToolResult:
        base_roi = estimate_roi(
            purchase_price=params.purchase_price,
            holding_period_years=params.holding_period_years,
            annual_appreciation_rate=params.base_appreciation_rate,
            annual_rental_yield_rate=params.base_rental_yield,
            property_id=params.property_id,
        )

        scenarios = run_scenario_analysis(
            purchase_price=params.purchase_price,
            baseline_roi=base_roi,
        )

        summary_lines = [
            f"Scenario '{s.scenario_name}': Projected Value = {s.financial_outcome.projected_exit_value:,.0f} EGP, "
            f"Total ROI = {s.financial_outcome.total_roi_percentage:.1f}% (Delta vs Base: {s.comparison_to_base_delta_pct:+.1f}%)"
            for s in scenarios
        ]

        evidence = [
            EvidenceRecord(
                evidence_id=f"E-CALC-SCENARIO-{params.property_id}",
                task_id="T_FIN_SCENARIO",
                source_type="financial_calculation",
                source_reference="ScenarioEngine.run_scenario_analysis",
                retrieval_method="sensitivity_matrix",
                content=f"Sensitivity Analysis for {params.property_id}: " + "; ".join(summary_lines),
                metadata={"scenarios": [s.model_dump() for s in scenarios]},
            )
        ]

        return ToolResult(
            success=True,
            data=[s.model_dump() for s in scenarios],
            evidence_records=evidence,
        )
