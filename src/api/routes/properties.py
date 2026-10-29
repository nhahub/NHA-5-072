from fastapi import APIRouter, HTTPException
from src.api.schemas import PropertySearchRequest
from src.tools.property_search import PropertySearchTool, PropertySearchParams
from src.tools.property_details import PropertyDetailsTool, PropertyDetailsParams

router = APIRouter(prefix="/properties", tags=["Properties"])

search_tool = PropertySearchTool()
details_tool = PropertyDetailsTool()

@router.post("/search")
def search_properties(req: PropertySearchRequest) -> list[dict]:
    params = PropertySearchParams(
        location=req.location,
        property_type=req.property_type,
        min_price=req.min_price,
        max_price=req.max_price,
        bedrooms=req.bedrooms,
        developer_name=req.developer_name,
        max_results=10,
    )
    res = search_tool.execute(params)
    if not res.success:
        raise HTTPException(status_code=500, detail=res.error_message)
    return res.data

@router.get("/{property_id}")
def get_property_details(property_id: str) -> dict:
    params = PropertyDetailsParams(property_id=property_id)
    res = details_tool.execute(params)
    if not res.success:
        raise HTTPException(status_code=404, detail=res.error_message)
    return res.data
