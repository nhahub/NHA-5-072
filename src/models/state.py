from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
from src.models.evidence import EvidenceArsenal
from src.models.research import ResearchPlan, UserPreferences
from src.models.property import PropertyListing
from src.models.financial import FinancialAnalysis
from src.models.report import DraftReport, FinalReport
from src.models.critique import CritiqueResult

class WorkflowPhase(str, Enum):
    PLANNING = "planning"
    RESEARCHING = "researching"
    ANALYZING = "analyzing"
    WRITING = "writing"
    CRITIQUING = "critiquing"
    COMPLETE = "complete"
    FAILED = "failed"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"

class GraphState(BaseModel):
    """Central typed state schema for the LangGraph multi-agent workflow."""

    # --- User Request & Session ---
    user_query: str
    session_id: str = "default_session"
    user_preferences: UserPreferences = Field(default_factory=UserPreferences)

    # --- Bounded Autonomy & Control ---
    phase: WorkflowPhase = WorkflowPhase.PLANNING
    iteration_count: int = 0
    max_iterations: int = 10
    retry_count: int = 0
    max_retries: int = 3
    total_tokens_used: int = 0
    token_budget: int = 100_000
    error_log: list[str] = Field(default_factory=list)
    agent_trajectory: list[dict[str, Any]] = Field(default_factory=list)

    # --- Planner Artifacts ---
    research_plan: ResearchPlan | None = None

    # --- Researcher Artifacts ---
    evidence_arsenal: EvidenceArsenal = Field(default_factory=EvidenceArsenal)
    completed_task_ids: list[str] = Field(default_factory=list)
    pending_task_ids: list[str] = Field(default_factory=list)

    # --- Domain Results ---
    property_results: list[PropertyListing] = Field(default_factory=list)
    financial_results: list[FinancialAnalysis] = Field(default_factory=list)
    comparison_matrix: dict[str, Any] = Field(default_factory=dict)

    # --- Writer Artifacts ---
    draft_report: DraftReport | None = None

    # --- Critic Artifacts ---
    critique: CritiqueResult | None = None
    critique_history: list[CritiqueResult] = Field(default_factory=list)

    # --- Final Output ---
    final_report: FinalReport | None = None
