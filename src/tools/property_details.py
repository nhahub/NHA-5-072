import json
from pathlib import Path
from pydantic import BaseModel, Field
from src.tools.base import BaseTool, ToolResult
from src.models.property import PropertyListing
from src.models.evidence import EvidenceRecord
from config.settings import settings

class PropertyDetailsParams(BaseModel):
    property_id: str = Field(description="Unique property identifier, e.g. 'PROP_001'")

class PropertyDetailsTool(BaseTool):
    name = "PropertyDetailsTool"
    description = "Retrieves full details, specifications, and payment plans for a single property ID."
    parameters_schema = PropertyDetailsParams

    def __init__(self, data_path: Path | None = None) -> None:
        self.data_path = data_path or (settings.RAW_DATA_DIR / "properties.json")
        self._cache: dict[str, PropertyListing] | None = None

    def _load_data(self) -> dict[str, PropertyListing]:
        if self._cache is not None:
            return self._cache
        if not self.data_path.exists():
            return {}
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            self._cache = {item["property_id"]: PropertyListing(**item) for item in raw}
            return self._cache

    def execute(self, params: PropertyDetailsParams) -> ToolResult:
        listings_map = self._load_data()
        prop = listings_map.get(params.property_id.strip())

        if not prop:
            return ToolResult(
                success=False,
                error_message=f"Property with ID '{params.property_id}' not found in registry.",
            )

        plans_str = "; ".join([
            f"{p.plan_name}: DP {p.down_payment_percentage:.0f}% ({p.down_payment_amount:,.0f} EGP), "
            f"{p.number_of_installments} {p.installment_frequency} installments of {p.installment_amount:,.0f} EGP over {p.duration_years} yrs"
            for p in prop.payment_plans
        ]) or "No payment plans specified."

        evidence_content = (
            f"Detailed Record for {prop.property_id} ({prop.project_name} by {prop.developer_name}): "
            f"Type: {prop.property_type}, Location: {prop.location} ({prop.sub_location or 'N/A'}), "
            f"Area: {prop.area_sqm} sqm, Bedrooms: {prop.bedrooms}, Bathrooms: {prop.bathrooms}, "
            f"Finishing: {prop.finishing or 'N/A'}, Price: {prop.price:,.0f} EGP, "
            f"Available Payment Plans: [{plans_str}]. Amenities: {', '.join(prop.amenities)}."
        )

        evidence = [
            EvidenceRecord(
                evidence_id=f"E-DET-{prop.property_id}",
                task_id="T_PROP_DETAILS",
                source_type="property_tool",
                source_reference=f"properties.json#{prop.property_id}",
                retrieval_method="id_lookup",
                content=evidence_content,
                metadata=prop.model_dump(),
            )
        ]

        return ToolResult(
            success=True,
            data=prop.model_dump(),
            evidence_records=evidence,
        )
