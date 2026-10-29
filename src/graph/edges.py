from src.models.state import GraphState

def route_after_research(state: GraphState) -> str:
    """Decides whether to proceed to financial analysis or terminate early."""
    if len(state.evidence_arsenal.records) == 0:
        return "insufficient_evidence"
    return "analyze"

def route_after_critique(state: GraphState) -> str:
    """Evaluates Critic verdict with strict retry caps and token bounds."""
    if not state.critique:
        return "finalize"

    if state.critique.verdict in ("accept", "accept_with_notes"):
        return "finalize"

    # Enforce Bounded Autonomy Guardrails
    if state.retry_count >= state.max_retries:
        state.error_log.append(f"Critic retry cap reached ({state.max_retries}). Forcing graceful exit.")
        return "insufficient_evidence"

    if state.iteration_count >= state.max_iterations:
        state.error_log.append(f"Max graph iteration cap reached ({state.max_iterations}). Forcing graceful exit.")
        return "insufficient_evidence"

    if state.total_tokens_used >= state.token_budget:
        state.error_log.append(f"Token budget exhausted ({state.total_tokens_used}/{state.token_budget}). Forcing graceful exit.")
        return "insufficient_evidence"

    # Re-route for targeted re-research
    state.retry_count += 1
    return "research"
