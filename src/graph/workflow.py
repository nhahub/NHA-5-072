from typing import Any
from langgraph.graph import StateGraph, END
from src.models.state import GraphState
from src.graph.nodes import (
    plan_node,
    research_node,
    analyze_node,
    write_node,
    critique_node,
    finalize_node,
    insufficient_evidence_node,
)
from src.graph.edges import route_after_research, route_after_critique

def build_workflow() -> Any:
    """Builds and compiles the cyclic multi-agent LangGraph workflow for Atlas AQAR."""
    graph = StateGraph(GraphState)

    # Add Nodes
    graph.add_node("plan", plan_node)
    graph.add_node("research", research_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("write", write_node)
    graph.add_node("critique", critique_node)
    graph.add_node("finalize", finalize_node)
    graph.add_node("insufficient_evidence", insufficient_evidence_node)

    # Set Entry Point
    graph.set_entry_point("plan")

    # Connect Edges
    graph.add_edge("plan", "research")
    graph.add_conditional_edges(
        "research",
        route_after_research,
        {
            "analyze": "analyze",
            "insufficient_evidence": "insufficient_evidence",
        },
    )
    graph.add_edge("analyze", "write")
    graph.add_edge("write", "critique")
    graph.add_conditional_edges(
        "critique",
        route_after_critique,
        {
            "finalize": "finalize",
            "research": "research",
            "insufficient_evidence": "insufficient_evidence",
        },
    )
    graph.add_edge("finalize", END)
    graph.add_edge("insufficient_evidence", END)

    return graph.compile()
