from fastapi import APIRouter
from src.api.schemas import InstallmentRequest, ROIRequest
from src.tools.installment_calc import InstallmentCalcTool, InstallmentCalcParams
from src.tools.roi_estimator import ROIEstimatorTool, ROIEstimatorParams
from src.tools.scenario_analyzer import ScenarioAnalyzerTool, ScenarioAnalyzerParams

router = APIRouter(prefix="/financial", tags=["Financial"])

inst_tool = InstallmentCalcTool()
roi_tool = ROIEstimatorTool()
scenario_tool = ScenarioAnalyzerTool()

@router.post("/installments")
def calculate_installments(req: InstallmentRequest) -> dict:
    params = InstallmentCalcParams(
        total_price=req.total_price,
        down_payment_pct=req.down_payment_pct,
        duration_years=req.duration_years,
        frequency=req.frequency,
        interest_rate=req.interest_rate,
        property_id=req.property_id,
    )
    res = inst_tool.execute(params)
    return res.data

@router.post("/roi")
def estimate_property_roi(req: ROIRequest) -> dict:
    params = ROIEstimatorParams(
        purchase_price=req.purchase_price,
        holding_period_years=req.holding_period_years,
        annual_appreciation_rate=req.annual_appreciation_rate,
        annual_rental_yield_rate=req.annual_rental_yield_rate,
        property_id=req.property_id,
    )
    res = roi_tool.execute(params)
    return res.data

@router.post("/scenarios")
def analyze_scenarios(req: ROIRequest) -> list[dict]:
    params = ScenarioAnalyzerParams(
        purchase_price=req.purchase_price,
        base_appreciation_rate=req.annual_appreciation_rate,
        base_rental_yield=req.annual_rental_yield_rate or 0.07,
        holding_period_years=req.holding_period_years,
        property_id=req.property_id,
    )
    res = scenario_tool.execute(params)
    return res.data
