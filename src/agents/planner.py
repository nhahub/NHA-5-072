import re
import uuid
from typing import Any
from src.models.research import ResearchPlan, ResearchTask, UserPreferences
from src.agents.prompts import load_prompt

class PlannerAgent:
    """
    Planner Agent that decomposes natural-language investment requests
    into 3 to 6 dependency-mapped, prioritized research tasks.
    """

    def __init__(self) -> None:
        self.system_prompt = load_prompt("planner")

    def plan(self, query: str, preferences: UserPreferences | None = None) -> ResearchPlan:
        """Decomposes the query into a structured ResearchPlan."""
        pref = preferences or UserPreferences()
        extracted_constraints = self._extract_constraints(query, pref)

        tasks: list[ResearchTask] = []

        # Task 1: Property Search
        tasks.append(
            ResearchTask(
                task_id="T01",
                description=f"Search properties matching criteria in {extracted_constraints.get('locations', ['Egypt'])[0]} with budget ~{extracted_constraints.get('budget_max', 'flexible')} EGP.",
                priority=1,
                task_type="property_search",
                dependencies=[],
                required_tools=["PropertySearchTool", "WebSearchTool"],
                completion_criteria="Discover 1 to 5 matching property listings with pricing and locations.",
            )
        )

        # Task 2: Property Specifications & Payment Plans
        tasks.append(
            ResearchTask(
                task_id="T02",
                description="Retrieve granular unit specifications, delivery horizon, and payment schedules for shortlisted listings.",
                priority=2,
                task_type="property_details",
                dependencies=["T01"],
                required_tools=["PropertyDetailsTool"],
                completion_criteria="Identify down payment percentage, installment frequencies, and handover dates.",
            )
        )

        # Task 3: Developer Due Diligence
        tasks.append(
            ResearchTask(
                task_id="T03",
                description="Investigate developer solvency, delivery track record, official website, and corporate reputation.",
                priority=3,
                task_type="developer_research",
                dependencies=["T01"],
                required_tools=["DeveloperLookupTool", "WebSearchTool", "WebScraperTool"],
                completion_criteria="Verify delivered unit volume, developer website status, and financial stability rating.",
            )
        )

        # Task 4: Deterministic Financial & ROI Modeling
        tasks.append(
            ResearchTask(
                task_id="T04",
                description="Compute amortization schedules, down payments, and 5-year capital appreciation / rental yield projections.",
                priority=4,
                task_type="financial_analysis",
                dependencies=["T02"],
                required_tools=["InstallmentCalcTool", "ROIEstimatorTool", "ScenarioAnalyzerTool"],
                completion_criteria="Generate exact installment schedules and net ROI percentages.",
            )
        )

        # Task 5: Market Context & Macro Drivers
        tasks.append(
            ResearchTask(
                task_id="T05",
                description="Retrieve regional market reports, live internet search on infrastructure catalysts (e.g. monorail, roads), and price appreciation dynamics.",
                priority=5,
                task_type="market_research",
                dependencies=["T01"],
                required_tools=["WebSearchTool", "WebScraperTool", "RAGRetrieverTool"],
                completion_criteria="Obtain grounded macroeconomic and rental yield benchmarks.",
            )
        )

        execution_order = ["T01", "T02", "T03", "T05", "T04"]

        return ResearchPlan(
            plan_id=f"PLAN_{uuid.uuid4().hex[:8].upper()}",
            original_query=query,
            interpreted_intent="Multi-dimensional real estate investment and payment plan advisory.",
            constraints_extracted=extracted_constraints,
            tasks=tasks,
            execution_order=execution_order,
            estimated_complexity="moderate" if len(tasks) <= 5 else "complex",
        )

    def _extract_constraints(self, query: str, pref: UserPreferences) -> dict[str, Any]:
        constraints: dict[str, Any] = {}
        q = query.lower()

        # Extract locations
        locations = []
        loc_keywords = [
            "new cairo", "fifth settlement", "golden square", "sheikh zayed",
            "6th of october", "new administrative capital", "mostakbal city",
            "north coast", "ras el hekma", "sidi abdel rahman"
        ]
        for loc in loc_keywords:
            if loc in q:
                locations.append(loc.title())
        if pref.preferred_locations:
            locations.extend(pref.preferred_locations)
        constraints["locations"] = list(set(locations)) or ["New Cairo"]

        # Extract budget / numbers
        price_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:m|million|k|thousand)?", q)
        if "million" in q or "m" in q:
            m = re.search(r"(\d+(?:\.\d+)?)\s*(?:m|million)", q)
            if m:
                constraints["budget_max"] = float(m.group(1)) * 1_000_000
        elif pref.budget_max:
            constraints["budget_max"] = pref.budget_max

        # Bedrooms
        bed_match = re.search(r"(\d+)\s*(?:bed|bedroom|br)", q)
        if bed_match:
            constraints["bedrooms"] = int(bed_match.group(1))
        elif pref.min_bedrooms:
            constraints["bedrooms"] = pref.min_bedrooms

        return constraints
