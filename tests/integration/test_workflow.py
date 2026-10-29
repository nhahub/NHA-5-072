import pytest
from src.models.state import GraphState, WorkflowPhase
from src.models.research import UserPreferences
from src.graph.workflow import build_workflow

def test_full_agentic_workflow_execution():
    workflow = build_workflow()

    query = "Find a 3-bedroom apartment in New Cairo under 15 million EGP with 8-year payment plan and calculate projected ROI."
    prefs = UserPreferences(
        budget_max=15_000_000.0,
        preferred_locations=["New Cairo"],
        min_bedrooms=3,
        holding_period_years=5,
    )

    initial_state = GraphState(
        user_query=query,
        user_preferences=prefs,
    )

    final_output = workflow.invoke(initial_state)

    if isinstance(final_output, dict):
        state = GraphState(**final_output)
    else:
        state = final_output

    # 1. State completed
    assert state.phase in (WorkflowPhase.COMPLETE, WorkflowPhase.INSUFFICIENT_EVIDENCE)

    # 2. Research plan was constructed
    assert state.research_plan is not None
    assert len(state.research_plan.tasks) >= 3

    # 3. Evidence Arsenal gathered verifiable records
    assert len(state.evidence_arsenal.records) >= 3

    # 4. Draft report was synthesized
    assert state.draft_report is not None
    assert len(state.draft_report.sections) == 9

    # 5. Critic verified draft
    assert state.critique is not None
    assert state.critique.verdict in ("accept", "accept_with_notes")

    # 6. Final report generated
    assert state.final_report is not None
    assert state.final_report.query == query
    assert len(state.final_report.sections) == 9
