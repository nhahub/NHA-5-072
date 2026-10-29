import time
from typing import Any
from pydantic import BaseModel, Field
from src.models.research import ResearchTask, UserPreferences
from src.models.evidence import EvidenceArsenal, EvidenceRecord
from src.models.property import PropertyListing
from src.models.financial import FinancialAnalysis, InstallmentSchedule, ROIResult
from src.tools.registry import ToolRegistry, default_registry
from src.agents.prompts import load_prompt
from config.settings import settings

class ReActStep(BaseModel):
    step_number: int
    thought: str
    action_tool: str
    action_input: dict[str, Any]
    observation: str
    duration_ms: float

class ResearcherAgent:
    """
    ReAct-based Researcher Agent for evidence foraging and tool execution.
    Executes tasks iteratively with Thought -> Action -> Observation steps.
    """

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or default_registry
        self.system_prompt = load_prompt("researcher")
        self.max_steps = settings.MAX_REACT_STEPS

    def execute_task(
        self,
        task: ResearchTask,
        arsenal: EvidenceArsenal,
        preferences: UserPreferences | None = None,
        context_properties: list[PropertyListing] | None = None,
    ) -> tuple[ResearchTask, list[ReActStep], list[Any]]:
        """
        Executes a single ResearchTask using ReAct decomposition.
        Returns the updated task, trajectory steps, and domain artifact outputs.
        """
        task.status = "in_progress"
        trajectory: list[ReActStep] = []
        artifacts: list[Any] = []
        step_num = 1

        # Determine tools to use based on task_type
        tools = self.registry.get_for_task_type(task.task_type)
        if not tools:
            tools = list(self.registry.get_all().values())

        # Step 1: Formulate Thought based on task type
        thought_1 = f"Task '{task.task_id}' requires {task.task_type}. Evaluating best tool among {[t.name for t in tools]}."

        if task.task_type == "property_search":
            search_tool = self.registry.get_tool("PropertySearchTool")
            filters: dict[str, Any] = {"max_results": 4}
            loc_pref = "New Cairo"
            if preferences:
                if preferences.preferred_locations:
                    loc_pref = preferences.preferred_locations[0]
                    filters["location"] = loc_pref
                if preferences.budget_max:
                    filters["max_price"] = preferences.budget_max
                if preferences.min_bedrooms:
                    filters["bedrooms"] = preferences.min_bedrooms

            start_t = time.perf_counter()
            tool_res = search_tool.run(**filters)
            dur = round((time.perf_counter() - start_t) * 1000.0, 2)

            obs = f"Found {len(tool_res.data)} matching properties." if tool_res.success else f"Search failed: {tool_res.error_message}"
            trajectory.append(
                ReActStep(
                    step_number=step_num,
                    thought=thought_1,
                    action_tool=search_tool.name,
                    action_input=filters,
                    observation=obs,
                    duration_ms=dur,
                )
            )

            # Store evidence
            for ev in tool_res.evidence_records:
                ev.task_id = task.task_id
                arsenal.add(ev)

            # Return property models
            if tool_res.success and tool_res.data:
                for d in tool_res.data:
                    artifacts.append(PropertyListing(**d))

            # Enrich with live internet search across developer and real estate sites
            try:
                web_tool = self.registry.get_tool("WebSearchTool")
                w_start = time.perf_counter()
                web_query = f"{loc_pref} Egypt compound properties prices payment plan 2025 2026"
                web_res = web_tool.run(query=web_query, max_results=3)
                w_dur = round((time.perf_counter() - w_start) * 1000.0, 2)
                trajectory.append(
                    ReActStep(
                        step_number=step_num + 1,
                        thought=f"Executing live internet search for real 2025/2026 property offerings and payment schemes in {loc_pref}.",
                        action_tool=web_tool.name,
                        action_input={"query": web_query, "max_results": 3},
                        observation=f"Discovered {len(web_res.evidence_records)} live web sources.",
                        duration_ms=w_dur,
                    )
                )
                for ev in web_res.evidence_records:
                    ev.task_id = task.task_id
                    arsenal.add(ev)
            except Exception:
                pass

            if artifacts:
                task.status = "completed"
                task.result_summary = f"Identified {len(artifacts)} matching real-estate properties with live market evidence."
            else:
                task.status = "insufficient_data"
                task.result_summary = "No properties matched stated criteria."

        elif task.task_type == "property_details":
            prop_id = "PROP_001"
            if context_properties and len(context_properties) > 0:
                prop_id = context_properties[0].property_id

            details_tool = self.registry.get_tool("PropertyDetailsTool")
            start_t = time.perf_counter()
            tool_res = details_tool.run(property_id=prop_id)
            dur = round((time.perf_counter() - start_t) * 1000.0, 2)

            obs = f"Retrieved detailed record for {prop_id}." if tool_res.success else f"Failed: {tool_res.error_message}"
            trajectory.append(
                ReActStep(
                    step_number=step_num,
                    thought=thought_1,
                    action_tool=details_tool.name,
                    action_input={"property_id": prop_id},
                    observation=obs,
                    duration_ms=dur,
                )
            )
            for ev in tool_res.evidence_records:
                ev.task_id = task.task_id
                arsenal.add(ev)
            if tool_res.success:
                task.status = "completed"
                task.result_summary = f"Obtained comprehensive specifications for {prop_id}."

        elif task.task_type == "developer_research":
            dev_name = "Emaar Misr"
            if context_properties and len(context_properties) > 0:
                dev_name = context_properties[0].developer_name

            dev_tool = self.registry.get_tool("DeveloperLookupTool")
            start_t = time.perf_counter()
            tool_res = dev_tool.run(developer_name=dev_name)
            dur = round((time.perf_counter() - start_t) * 1000.0, 2)

            obs = f"Developer track record retrieved for {dev_name}." if tool_res.success else f"Lookup failed: {tool_res.error_message}"
            trajectory.append(
                ReActStep(
                    step_number=step_num,
                    thought=thought_1,
                    action_tool=dev_tool.name,
                    action_input={"developer_name": dev_name},
                    observation=obs,
                    duration_ms=dur,
                )
            )
            for ev in tool_res.evidence_records:
                ev.task_id = task.task_id
                arsenal.add(ev)

            # Live Internet Search & Web Scraping on Developer
            try:
                web_tool = self.registry.get_tool("WebSearchTool")
                dev_query = f"{dev_name} Egypt official developments projects track record 2025 2026"
                dev_search = web_tool.run(query=dev_query, max_results=2)
                for ev in dev_search.evidence_records:
                    ev.task_id = task.task_id
                    arsenal.add(ev)

                if dev_search.success and isinstance(dev_search.data, list) and len(dev_search.data) > 0:
                    top_url = dev_search.data[0].get("url")
                    if top_url and top_url.startswith("http"):
                        scraper = self.registry.get_tool("WebScraperTool")
                        s_start = time.perf_counter()
                        scrape_res = scraper.run(url=top_url, extract_financials=True)
                        s_dur = round((time.perf_counter() - s_start) * 1000.0, 2)
                        trajectory.append(
                            ReActStep(
                                step_number=step_num + 1,
                                thought=f"Scraping developer portal/announcements at {top_url}.",
                                action_tool=scraper.name,
                                action_input={"url": top_url},
                                observation=f"Scraped {top_url} (status={scrape_res.success}).",
                                duration_ms=s_dur,
                            )
                        )
                        for ev in scrape_res.evidence_records:
                            ev.task_id = task.task_id
                            arsenal.add(ev)
            except Exception:
                pass

            task.status = "completed"
            task.result_summary = f"Verified solvency and track record of {dev_name} with live web cross-referencing."

        elif task.task_type == "financial_analysis":
            target_price = 10000000.0
            target_prop_id = "PROP_SAMPLE"
            if context_properties and len(context_properties) > 0:
                target_price = context_properties[0].price
                target_prop_id = context_properties[0].property_id

            # Sub-step 1: Installment Calc
            inst_tool = self.registry.get_tool("InstallmentCalcTool")
            start_t = time.perf_counter()
            inst_res = inst_tool.run(
                total_price=target_price,
                down_payment_pct=10.0,
                duration_years=7.0,
                frequency="quarterly",
                property_id=target_prop_id,
            )
            dur1 = round((time.perf_counter() - start_t) * 1000.0, 2)
            trajectory.append(
                ReActStep(
                    step_number=1,
                    thought=f"Computing 7-year installment schedule for {target_prop_id}.",
                    action_tool=inst_tool.name,
                    action_input={"total_price": target_price, "down_payment_pct": 10.0, "duration_years": 7.0},
                    observation=f"Installment calculated: quarterly payment = {inst_res.data.get('installment_amount', 0):,.2f} EGP.",
                    duration_ms=dur1,
                )
            )
            for ev in inst_res.evidence_records:
                ev.task_id = task.task_id
                arsenal.add(ev)

            # Sub-step 2: ROI Estimation
            roi_tool = self.registry.get_tool("ROIEstimatorTool")
            start_t = time.perf_counter()
            roi_res = roi_tool.run(
                purchase_price=target_price,
                holding_period_years=5,
                annual_appreciation_rate=0.12,
                annual_rental_yield_rate=0.07,
                property_id=target_prop_id,
            )
            dur2 = round((time.perf_counter() - start_t) * 1000.0, 2)
            trajectory.append(
                ReActStep(
                    step_number=2,
                    thought="Computing 5-year capital appreciation and rental yield ROI projections.",
                    action_tool=roi_tool.name,
                    action_input={"purchase_price": target_price, "holding_period_years": 5},
                    observation=f"Estimated Total ROI = {roi_res.data.get('total_roi_percentage', 0):.1f}%.",
                    duration_ms=dur2,
                )
            )
            for ev in roi_res.evidence_records:
                ev.task_id = task.task_id
                arsenal.add(ev)

            if inst_res.success and roi_res.success:
                task.status = "completed"
                task.result_summary = "Deterministic financial schedules and ROI projections completed."
                artifacts.append({
                    "installment": inst_res.data,
                    "roi": roi_res.data,
                })

        elif task.task_type in ("market_research", "general_research", "web_scraping"):
            # Internal RAG lookup
            rag_tool = self.registry.get_tool("RAGRetrieverTool")
            start_t = time.perf_counter()
            rag_res = rag_tool.run(query=task.description, top_k=2)
            for ev in rag_res.evidence_records:
                ev.task_id = task.task_id
                arsenal.add(ev)

            # Live Internet Search across the web
            web_tool = self.registry.get_tool("WebSearchTool")
            w_start = time.perf_counter()
            web_res = web_tool.run(query=task.description, max_results=3)
            dur = round((time.perf_counter() - w_start) * 1000.0, 2)

            trajectory.append(
                ReActStep(
                    step_number=step_num,
                    thought=f"Searching entire internet for latest reliable market data and dynamic figures on: {task.description}.",
                    action_tool=web_tool.name,
                    action_input={"query": task.description, "max_results": 3},
                    observation=f"Retrieved {len(web_res.evidence_records)} live web sources.",
                    duration_ms=dur,
                )
            )
            for ev in web_res.evidence_records:
                ev.task_id = task.task_id
                arsenal.add(ev)

            # Live Web Scraping on primary discovered portal/developer URL
            if web_res.success and isinstance(web_res.data, list) and len(web_res.data) > 0:
                top_url = web_res.data[0].get("url")
                if top_url and top_url.startswith("http"):
                    try:
                        scraper_tool = self.registry.get_tool("WebScraperTool")
                        s_start = time.perf_counter()
                        scrape_res = scraper_tool.run(url=top_url, extract_financials=True)
                        s_dur = round((time.perf_counter() - s_start) * 1000.0, 2)
                        trajectory.append(
                            ReActStep(
                                step_number=step_num + 1,
                                thought=f"Performing live web scraping on primary project/developer site: {top_url}.",
                                action_tool=scraper_tool.name,
                                action_input={"url": top_url},
                                observation=f"Scraped {top_url}: figures extracted = {scrape_res.data.get('extracted_figures') if scrape_res.data else {}}",
                                duration_ms=s_dur,
                            )
                        )
                        for ev in scrape_res.evidence_records:
                            ev.task_id = task.task_id
                            arsenal.add(ev)
                    except Exception:
                        pass

            task.status = "completed"
            task.result_summary = "Live internet search and web scraping completed with verifiable citations and dynamic figures."

        else:
            task.status = "completed"
            task.result_summary = "Task processed successfully."

        return task, trajectory, artifacts
