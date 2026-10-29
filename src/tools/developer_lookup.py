import json
from pathlib import Path
from pydantic import BaseModel, Field
from src.tools.base import BaseTool, ToolResult
from src.models.property import Developer
from src.models.evidence import EvidenceRecord
from config.settings import settings

class DeveloperLookupParams(BaseModel):
    developer_name: str = Field(description="Name or substring of the real estate developer")

class DeveloperLookupTool(BaseTool):
    name = "DeveloperLookupTool"
    description = "Retrieves developer track record, delivered units, reputation notes, and solvency ratings."
    parameters_schema = DeveloperLookupParams

    def __init__(self, data_path: Path | None = None) -> None:
        self.data_path = data_path or (settings.RAW_DATA_DIR / "developers.json")
        self._cache: list[Developer] | None = None

    def _load_data(self) -> list[Developer]:
        if self._cache is not None:
            return self._cache
        if not self.data_path.exists():
            return []
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            self._cache = [Developer(**item) for item in raw]
            return self._cache

    def execute(self, params: DeveloperLookupParams) -> ToolResult:
        developers = self._load_data()
        query = params.developer_name.lower().strip()

        matched = [d for d in developers if query in d.name.lower()]

        if not matched:
            return ToolResult(
                success=False,
                error_message=f"No developer profile matching '{params.developer_name}' found.",
            )

        dev = matched[0]
        units_str = f"{dev.total_delivered_units:,}" if dev.total_delivered_units else "N/A"
        content_desc = (
            f"Developer Profile: {dev.name} (Established {dev.established_year or 'N/A'}, HQ: {dev.headquarters or 'N/A'}). "
            f"Delivered Units: ~{units_str}. "
            f"Financial Solvency Rating: {dev.financial_solvency_rating or 'Unrated'}. "
            f"Notable Projects: {', '.join(dev.notable_projects)}. "
            f"Reputation Analysis: {dev.reputation_notes or 'Established market presence.'}"
        )

        evidence = [
            EvidenceRecord(
                evidence_id=f"E-DEV-{dev.developer_id}",
                task_id="T_DEV_LOOKUP",
                source_type="developer_tool",
                source_reference=f"developers.json#{dev.developer_id}",
                retrieval_method="name_lookup",
                content=content_desc,
                metadata=dev.model_dump(),
            )
        ]

        return ToolResult(
            success=True,
            data=dev.model_dump(),
            evidence_records=evidence,
        )
