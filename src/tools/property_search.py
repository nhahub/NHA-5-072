import json
from pathlib import Path
from pydantic import BaseModel, Field
from src.tools.base import BaseTool, ToolResult
from src.models.property import PropertyListing, PropertyFilter
from src.models.evidence import EvidenceRecord
from config.settings import settings

class PropertySearchParams(BaseModel):
    location: str | None = Field(default=None, description="Location/city filter, e.g. 'New Cairo', 'Sheikh Zayed'")
    sub_location: str | None = Field(default=None, description="Sub-district, e.g. 'Golden Square'")
    property_type: str | None = Field(default=None, description="Type: apartment, villa, townhouse, duplex, chalet")
    min_price: float | None = Field(default=None, description="Minimum price in EGP")
    max_price: float | None = Field(default=None, description="Maximum price in EGP")
    min_area_sqm: float | None = Field(default=None, description="Minimum area in sqm")
    bedrooms: int | None = Field(default=None, description="Number of bedrooms")
    developer_name: str | None = Field(default=None, description="Developer name")
    max_results: int = Field(default=5, description="Maximum number of results to return")

class PropertySearchTool(BaseTool):
    name = "PropertySearchTool"
    description = "Searches verified real-estate property listings using specific query filters."
    parameters_schema = PropertySearchParams

    def __init__(self, data_path: Path | None = None) -> None:
        self.data_path = data_path or (settings.RAW_DATA_DIR / "properties.json")
        self._cache: list[PropertyListing] | None = None

    def _load_data(self) -> list[PropertyListing]:
        if self._cache is not None:
            return self._cache
        if not self.data_path.exists():
            return []
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            self._cache = [PropertyListing(**item) for item in raw]
            return self._cache

    def execute(self, params: PropertySearchParams) -> ToolResult:
        listings = self._load_data()
        results: list[PropertyListing] = []

        for p in listings:
            if params.location and params.location.lower() not in p.location.lower():
                continue
            if params.sub_location and p.sub_location and params.sub_location.lower() not in p.sub_location.lower():
                continue
            if params.property_type and params.property_type.lower() != p.property_type.lower():
                continue
            if params.min_price is not None and p.price < params.min_price:
                continue
            if params.max_price is not None and p.price > params.max_price:
                continue
            if params.min_area_sqm is not None and p.area_sqm < params.min_area_sqm:
                continue
            if params.bedrooms is not None and (p.bedrooms is None or p.bedrooms < params.bedrooms):
                continue
            if params.developer_name and params.developer_name.lower() not in p.developer_name.lower():
                continue
            results.append(p)
            if len(results) >= params.max_results:
                break

        evidence: list[EvidenceRecord] = []
        for r in results:
            content_desc = (
                f"Property {r.property_id}: {r.project_name} by {r.developer_name} located in {r.location} "
                f"({r.sub_location or 'N/A'}). Type: {r.property_type}, Area: {r.area_sqm} sqm, "
                f"Bedrooms: {r.bedrooms}, Price: {r.price:,.0f} EGP ({r.price_per_sqm:,.0f} EGP/sqm). "
                f"Delivery: {r.delivery_date or 'TBD'}."
            )
            evidence.append(
                EvidenceRecord(
                    evidence_id=f"E-PROP-{r.property_id}",
                    task_id="T_PROP_SEARCH",
                    source_type="property_tool",
                    source_reference=f"properties.json#{r.property_id}",
                    retrieval_method="metadata_filter",
                    content=content_desc,
                    metadata={"property_id": r.property_id, "price": r.price, "location": r.location},
                )
            )

        return ToolResult(
            success=True,
            data=[r.model_dump() for r in results],
            evidence_records=evidence,
        )
