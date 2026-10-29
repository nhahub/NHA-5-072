from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field

class EvidenceRecord(BaseModel):
    """A single piece of retrieved or computed evidence with full provenance."""
    evidence_id: str = Field(description="Unique identifier, e.g. E001")
    task_id: str = Field(description="ID of the research task that gathered this evidence")
    source_type: Literal[
        "rag_retrieval",
        "web_search",
        "web_scraping",
        "property_tool",
        "developer_tool",
        "financial_calculation",
        "user_provided",
        "derived"
    ]
    source_reference: str = Field(description="Origin: URL, document title, tool name, or database table")
    retrieval_method: str = Field(default="direct", description="e.g. semantic_search, metadata_filter, formula")
    content: str = Field(description="Verifiable factual text or structured summary")
    metadata: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    date_of_source: str | None = Field(default=None, description="Publication or listing date if known")

class EvidenceArsenal(BaseModel):
    """Collection and index of all evidence gathered during the research lifecycle."""
    records: list[EvidenceRecord] = Field(default_factory=list)

    def add(self, record: EvidenceRecord) -> None:
        """Add record, auto-assigning evidence_id if missing or generic."""
        if not record.evidence_id or record.evidence_id.startswith("TEMP"):
            idx = len(self.records) + 1
            record.evidence_id = f"E{idx:03d}"
        self.records.append(record)

    def get_by_id(self, evidence_id: str) -> EvidenceRecord | None:
        for r in self.records:
            if r.evidence_id == evidence_id:
                return r
        return None

    def get_by_task(self, task_id: str) -> list[EvidenceRecord]:
        return [r for r in self.records if r.task_id == task_id]

    def get_by_type(self, source_type: str) -> list[EvidenceRecord]:
        return [r for r in self.records if r.source_type == source_type]

    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self.records:
            counts[r.source_type] = counts.get(r.source_type, 0) + 1
        return counts
