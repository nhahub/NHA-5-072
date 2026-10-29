from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field
from src.models.evidence import EvidenceArsenal

class CitedClaim(BaseModel):
    """An explicit claim linked directly to verifiable evidence IDs."""
    claim_text: str
    evidence_ids: list[str] = Field(default_factory=list)
    claim_type: Literal["factual", "calculated", "assumption", "opinion"] = "factual"

class ReportSection(BaseModel):
    """A distinct structural section of the final research report."""
    section_type: Literal[
        "executive_summary",
        "research_scope",
        "property_findings",
        "comparative_analysis",
        "financial_analysis",
        "market_context",
        "evidence_citations",
        "uncertainty_limitations",
        "final_synthesis"
    ]
    title: str
    content: str
    cited_claims: list[CitedClaim] = Field(default_factory=list)

class DraftReport(BaseModel):
    """A generated draft report ready for Critic scrutiny."""
    draft_number: int = 1
    sections: list[ReportSection] = Field(default_factory=list)
    total_claims: int = 0
    cited_claims_count: int = 0
    uncited_claims_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

class FinalReport(BaseModel):
    """The verified, citation-grounded final output product."""
    report_id: str
    query: str
    sections: list[ReportSection] = Field(default_factory=list)
    evidence_arsenal: EvidenceArsenal = Field(default_factory=EvidenceArsenal)
    metadata: dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
