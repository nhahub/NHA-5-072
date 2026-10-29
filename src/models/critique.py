from typing import Literal
from pydantic import BaseModel, Field

class CritiqueIssue(BaseModel):
    """A specific issue flagged during report critique."""
    issue_id: str
    category: Literal[
        "missing_evidence",
        "invalid_citation",
        "numerical_error",
        "constraint_violation",
        "unsupported_claim",
        "conflicting_sources",
        "incomplete_coverage",
        "formatting",
        "other"
    ]
    severity: Literal["critical", "major", "minor"]
    description: str
    affected_section: str | None = None
    suggested_action: str

class CritiqueResult(BaseModel):
    """The structured decision and evaluation output from the Critic."""
    critique_id: str
    draft_number: int
    verdict: Literal["accept", "reject", "accept_with_notes"]
    issues: list[CritiqueIssue] = Field(default_factory=list)
    re_research_tasks: list[str] = Field(default_factory=list, description="Task IDs to re-run or create")
    overall_score: float = Field(default=1.0, ge=0.0, le=1.0)
    summary: str
    evidence_coverage_pct: float = Field(default=100.0, ge=0.0, le=100.0)
    citation_precision_pct: float = Field(default=100.0, ge=0.0, le=100.0)
    financial_accuracy_pct: float = Field(default=100.0, ge=0.0, le=100.0)
