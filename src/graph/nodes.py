import uuid
from datetime import datetime, timezone
from src.models.state import GraphState, WorkflowPhase
from src.models.report import FinalReport
from src.agents.planner import PlannerAgent
from src.agents.researcher import ResearcherAgent
from src.agents.writer import WriterAgent
from src.agents.critic import CriticAgent
from src.engine.installments import calculate_installment_schedule
from src.engine.roi import estimate_roi
from src.engine.scenarios import run_scenario_analysis
from src.models.financial import FinancialAnalysis

planner = PlannerAgent()
researcher = ResearcherAgent()
writer = WriterAgent()
critic = CriticAgent()

def plan_node(state: GraphState) -> GraphState:
    """Planner node: Decomposes query into research tasks."""
    state.phase = WorkflowPhase.PLANNING
    state.iteration_count += 1
    state.total_tokens_used += 450

    plan = planner.plan(query=state.user_query, preferences=state.user_preferences)
    state.research_plan = plan
    state.pending_task_ids = [t.task_id for t in plan.tasks]

    state.agent_trajectory.append({
        "phase": "plan",
        "action": "Generated research plan",
        "tasks_count": len(plan.tasks),
        "execution_order": plan.execution_order,
    })
    return state

def research_node(state: GraphState) -> GraphState:
    """Researcher node: Executes tasks using ReAct loop and gathers evidence."""
    state.phase = WorkflowPhase.RESEARCHING
    state.iteration_count += 1
    state.total_tokens_used += 1200

    if not state.research_plan:
        return state

    for task in state.research_plan.tasks:
        if task.status in ("completed", "skipped"):
            continue

        updated_task, trajectory, outputs = researcher.execute_task(
            task=task,
            arsenal=state.evidence_arsenal,
            preferences=state.user_preferences,
            context_properties=state.property_results,
        )

        state.completed_task_ids.append(task.task_id)
        if task.task_id in state.pending_task_ids:
            state.pending_task_ids.remove(task.task_id)

        # Collect properties if found
        for out in outputs:
            if hasattr(out, "property_id") and out not in state.property_results:
                state.property_results.append(out)

        state.agent_trajectory.append({
            "phase": "research",
            "task_id": task.task_id,
            "task_type": task.task_type,
            "status": task.status,
            "steps_taken": len(trajectory),
        })

    return state

def analyze_node(state: GraphState) -> GraphState:
    """Analyzer node: Runs deterministic financial schedules and ROI sensitivity."""
    state.phase = WorkflowPhase.ANALYZING
    state.iteration_count += 1

    fin_results: list[FinancialAnalysis] = []
    for prop in state.property_results[:3]:
        # Installment schedule
        schedule = calculate_installment_schedule(
            total_price=prop.price,
            down_payment_pct=10.0,
            duration_years=7.0,
            property_id=prop.property_id,
        )
        # ROI baseline
        roi = estimate_roi(
            purchase_price=prop.price,
            holding_period_years=state.user_preferences.holding_period_years or 5,
            property_id=prop.property_id,
        )
        # Scenarios
        scenarios = run_scenario_analysis(purchase_price=prop.price, baseline_roi=roi)

        analysis = FinancialAnalysis(
            property_id=prop.property_id,
            selected_payment_plan=schedule,
            baseline_roi=roi,
            scenarios=scenarios,
        )
        fin_results.append(analysis)

    state.financial_results = fin_results
    state.agent_trajectory.append({
        "phase": "analyze",
        "properties_analyzed": len(fin_results),
    })
    return state

def write_node(state: GraphState) -> GraphState:
    """Writer node: Synthesizes draft report with explicit evidence citations."""
    state.phase = WorkflowPhase.WRITING
    state.iteration_count += 1
    state.total_tokens_used += 1800

    draft_num = (state.draft_report.draft_number + 1) if state.draft_report else 1

    if state.research_plan is None:
        state.research_plan = planner.plan(query=state.user_query, preferences=state.user_preferences)

    draft = writer.write_draft(
        query=state.user_query,
        plan=state.research_plan,
        arsenal=state.evidence_arsenal,
        properties=state.property_results,
        financials=state.financial_results,
        preferences=state.user_preferences,
        draft_number=draft_num,
    )
    state.draft_report = draft
    state.agent_trajectory.append({
        "phase": "write",
        "draft_number": draft_num,
        "sections_count": len(draft.sections),
    })
    return state

def critique_node(state: GraphState) -> GraphState:
    """Critic node: Verifies evidence coverage, citations, numbers, and constraints."""
    state.phase = WorkflowPhase.CRITIQUING
    state.iteration_count += 1
    state.total_tokens_used += 650

    if not state.draft_report or not state.research_plan:
        return state

    critique_result = critic.critique(
        draft=state.draft_report,
        arsenal=state.evidence_arsenal,
        plan=state.research_plan,
        preferences=state.user_preferences,
    )

    state.critique = critique_result
    state.critique_history.append(critique_result)

    state.agent_trajectory.append({
        "phase": "critique",
        "verdict": critique_result.verdict,
        "score": critique_result.overall_score,
        "issues_count": len(critique_result.issues),
    })
    return state

def finalize_node(state: GraphState) -> GraphState:
    """Finalize node: Packages the final verified research report."""
    state.phase = WorkflowPhase.COMPLETE

    if state.draft_report:
        report = FinalReport(
            report_id=f"REP_{uuid.uuid4().hex[:8].upper()}",
            query=state.user_query,
            sections=state.draft_report.sections,
            evidence_arsenal=state.evidence_arsenal,
            metadata={
                "total_tokens_used": state.total_tokens_used,
                "iterations": state.iteration_count,
                "retries": state.retry_count,
                "critic_score": state.critique.overall_score if state.critique else 1.0,
            },
            generated_at=datetime.now(timezone.utc),
        )
        state.final_report = report

    state.agent_trajectory.append({
        "phase": "finalize",
        "status": "success",
    })
    return state

def insufficient_evidence_node(state: GraphState) -> GraphState:
    """Graceful exit node when verifiable evidence is insufficient or budget is exhausted."""
    state.phase = WorkflowPhase.INSUFFICIENT_EVIDENCE
    state.error_log.append("Workflow terminated: insufficient evidence or budget bounds reached.")

    if state.draft_report:
        report = FinalReport(
            report_id=f"REP_INSUF_{uuid.uuid4().hex[:6].upper()}",
            query=state.user_query,
            sections=state.draft_report.sections,
            evidence_arsenal=state.evidence_arsenal,
            metadata={
                "status": "insufficient_evidence",
                "iterations": state.iteration_count,
                "retries": state.retry_count,
            },
            generated_at=datetime.now(timezone.utc),
        )
        state.final_report = report

    state.agent_trajectory.append({
        "phase": "insufficient_evidence",
        "status": "terminated_with_limitations",
    })
    return state
