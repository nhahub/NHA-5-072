import uuid
from fastapi import APIRouter, HTTPException
from src.api.schemas import ResearchRequest, ResearchResponse
from src.models.state import GraphState
from src.graph.workflow import build_workflow

router = APIRouter(prefix="/research", tags=["Research"])

# In-memory session store
_research_store: dict[str, GraphState] = {}
_workflow = build_workflow()

@router.post("", response_model=ResearchResponse)
def trigger_research(req: ResearchRequest) -> ResearchResponse:
    research_id = f"RES_{uuid.uuid4().hex[:8].upper()}"

    initial_state = GraphState(
        user_query=req.query,
        session_id=req.session_id or "default",
        user_preferences=req.preferences or initial_state.user_preferences if 'initial_state' in locals() else None,
    )
    if req.preferences:
        initial_state.user_preferences = req.preferences

    # Execute LangGraph workflow
    final_output = _workflow.invoke(initial_state)

    if isinstance(final_output, dict):
        final_state = GraphState(**final_output)
    else:
        final_state = final_output

    _research_store[research_id] = final_state

    return ResearchResponse(
        research_id=research_id,
        status=final_state.phase.value,
        final_report=final_state.final_report,
        evidence_count=len(final_state.evidence_arsenal.records),
        trajectory=final_state.agent_trajectory,
    )

@router.get("/{research_id}", response_model=ResearchResponse)
def get_research_status(research_id: str) -> ResearchResponse:
    state = _research_store.get(research_id)
    if not state:
        raise HTTPException(status_code=404, detail="Research session not found.")
    return ResearchResponse(
        research_id=research_id,
        status=state.phase.value,
        final_report=state.final_report,
        evidence_count=len(state.evidence_arsenal.records),
        trajectory=state.agent_trajectory,
    )

@router.get("/{research_id}/evidence")
def get_research_evidence(research_id: str) -> dict:
    state = _research_store.get(research_id)
    if not state:
        raise HTTPException(status_code=404, detail="Research session not found.")
    return state.evidence_arsenal.model_dump()
