import sys
from pathlib import Path

# Ensure workspace root is always in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import cast
from datetime import datetime

from src.models.state import GraphState
try:
    from src.models.research import UserPreferences, InvestmentGoal
except ImportError:
    from typing import Literal
    from src.models.research import UserPreferences  # type: ignore
    InvestmentGoal = Literal["capital_growth", "rental_yield", "personal_use", "balanced"]  # type: ignore
from src.graph.workflow import build_workflow
from src.tools.property_search import PropertySearchTool, PropertySearchParams
from src.tools.installment_calc import InstallmentCalcTool, InstallmentCalcParams
from src.tools.roi_estimator import ROIEstimatorTool, ROIEstimatorParams
from src.tools.scenario_analyzer import ScenarioAnalyzerTool, ScenarioAnalyzerParams
from src.tools.web_search import WebSearchTool, WebSearchParams
from src.tools.web_scraper import WebScraperTool, WebScraperParams

# Page Configuration
st.set_page_config(
    page_title="Atlas AQAR | Real-Estate Research Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #F9FAFB, #F3F4F6);
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .agent-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
        background-color: #E0E7FF;
        color: #3730A3;
    }
    .evidence-badge {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        padding: 2px 8px;
        border-radius: 6px;
        font-family: monospace;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# State initialization
if "workflow" not in st.session_state:
    st.session_state.workflow = build_workflow()
if "last_state" not in st.session_state:
    st.session_state.last_state = None

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/fluency/96/real-estate.png", width=64)
st.sidebar.title("Atlas AQAR")
st.sidebar.caption("Agentic Research & Investment System")
page = st.sidebar.radio(
    "Navigation",
    ["🔍 Research Console", "🏘️ Property Discovery", "💰 Financial Intelligence", "📋 Evidence Arsenal", "🌐 Live Web & Scraper", "📊 System Observability"]
)

st.sidebar.divider()
st.sidebar.subheader("Quick Configuration")
budget_max = st.sidebar.number_input("Budget Ceiling (EGP)", min_value=1_000_000, max_value=100_000_000, value=15_000_000, step=500_000)
pref_location = st.sidebar.selectbox("Target Location", ["Any Location", "New Cairo", "Sheikh Zayed", "New Administrative Capital", "Mostakbal City", "North Coast"])
investment_goal = cast(
    InvestmentGoal,
    st.sidebar.selectbox("Primary Objective", ["balanced", "capital_growth", "rental_yield", "personal_use"])
)
holding_years = st.sidebar.slider("Holding Period (Years)", 1, 15, 5)

# ---------------- PAGE 1: RESEARCH CONSOLE ----------------
if page == "🔍 Research Console":
    st.markdown('<div class="main-title">🏛️ Atlas AQAR Research Console</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Autonomous task decomposition, evidence foraging, deterministic financial modeling, and critique.</div>', unsafe_allow_html=True)

    default_prompt = "Find me a 3-bedroom apartment in New Cairo under 15M EGP with a 7 to 8-year payment plan and calculate projected 5-year ROI."
    query = st.text_area("Investment Research Inquiry:", value=default_prompt, height=90)

    col1, col2 = st.columns([1, 4])
    with col1:
        start_btn = st.button("🚀 Launch Autonomous Research", type="primary", use_container_width=True)

    if start_btn and query.strip():
        with st.spinner("Executing bounded multi-agent LangGraph workflow..."):
            prefs = UserPreferences(
                budget_max=float(budget_max),
                preferred_locations=[pref_location] if pref_location != "Any Location" else ["New Cairo"],
                investment_goal=investment_goal,
                holding_period_years=holding_years,
            )
            init_state = GraphState(
                user_query=query,
                user_preferences=prefs,
            )
            result = st.session_state.workflow.invoke(init_state)
            if isinstance(result, dict):
                st.session_state.last_state = GraphState(**result)
            else:
                st.session_state.last_state = result
            st.success("Research completed successfully!")

    if st.session_state.last_state:
        state: GraphState = st.session_state.last_state
        st.divider()

        # Top KPI Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Workflow Phase", state.phase.value.upper())
        m2.metric("Evidence Records", len(state.evidence_arsenal.records))
        m3.metric("Properties Discovered", len(state.property_results))
        score_val = f"{state.critique.overall_score * 100:.0f}%" if state.critique else "100%"
        m4.metric("Critic Quality Score", score_val)

        # Tabbed Results View
        t_report, t_plan, t_trajectory, t_critique = st.tabs(["📑 Verified Report", "🗺️ Research Plan", "🔄 Agent Trajectory", "🧐 Critic Verification"])

        with t_report:
            if state.final_report:
                st.subheader(f"Investment Advisory Report: {state.final_report.report_id}")
                st.caption(f"Generated at: {state.final_report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                for sec in state.final_report.sections:
                    with st.expander(sec.title, expanded=(sec.section_type in ("executive_summary", "property_findings", "financial_analysis"))):
                        st.markdown(sec.content)
                        if sec.cited_claims:
                            st.caption("Verifiable Claim Grounding:")
                            for c in sec.cited_claims:
                                badges = " ".join([f"`{eid}`" for eid in c.evidence_ids])
                                st.markdown(f"- *{c.claim_text}* → Supported by: {badges}")
            else:
                st.info("No report generated yet.")

        with t_plan:
            if state.research_plan:
                st.write(f"**Interpreted Intent:** {state.research_plan.interpreted_intent}")
                st.write(f"**Extracted Constraints:** `{state.research_plan.constraints_extracted}`")
                st.write("**Decomposed Research Tasks:**")
                for t in state.research_plan.tasks:
                    st.markdown(f"- **[{t.task_id}]** `{t.task_type}` (Priority {t.priority}): {t.description} — Status: `{t.status}`")

        with t_trajectory:
            st.write("Step-by-step agentic execution path:")
            for step in state.agent_trajectory:
                st.markdown(f"`{step.get('phase', 'agent').upper()}`: {step}")

        with t_critique:
            if state.critique:
                st.write(f"**Verdict:** `{state.critique.verdict}` (Score: {state.critique.overall_score * 100:.1f}%)")
                st.write(f"**Summary:** {state.critique.summary}")
                col_c1, col_c2, col_c3 = st.columns(3)
                col_c1.metric("Citation Precision", f"{state.critique.citation_precision_pct}%")
                col_c2.metric("Evidence Coverage", f"{state.critique.evidence_coverage_pct}%")
                col_c3.metric("Financial Accuracy", f"{state.critique.financial_accuracy_pct}%")
                if state.critique.issues:
                    st.write("**Issues Audit Log:**")
                    for iss in state.critique.issues:
                        st.warning(f"[{iss.severity.upper()}] {iss.category}: {iss.description} (Action: {iss.suggested_action})")

# ---------------- PAGE 2: PROPERTY DISCOVERY ----------------
elif page == "🏘️ Property Discovery":
    st.markdown('<div class="main-title">🏘️ Property Discovery & Comparative Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Explore verified real-estate project inventory and specs across East and West Cairo.</div>', unsafe_allow_html=True)

    tool = PropertySearchTool()
    search_params = PropertySearchParams(max_results=20)
    res = tool.execute(search_params)

    if res.success and res.data:
        df = pd.DataFrame(res.data)
        st.dataframe(
            df[["project_name", "developer_name", "location", "property_type", "area_sqm", "bedrooms", "price", "delivery_date"]],
            use_container_width=True
        )

        col1, col2 = st.columns(2)
        with col1:
            fig_price = px.bar(df, x="project_name", y="price", color="location", title="Property Price Comparison (EGP)")
            st.plotly_chart(fig_price, use_container_width=True)
        with col2:
            fig_sqm = px.scatter(df, x="area_sqm", y="price", size="bedrooms", color="developer_name", hover_name="project_name", title="Price vs. Area (sqm)")
            st.plotly_chart(fig_sqm, use_container_width=True)

# ---------------- PAGE 3: FINANCIAL INTELLIGENCE ----------------
elif page == "💰 Financial Intelligence":
    st.markdown('<div class="main-title">💰 Deterministic Financial Modeling</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Mathematical installment schedules, ROI projections, and sensitivity analysis.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Plan Parameters")
        p_price = st.number_input("Unit Total Price (EGP)", value=12_000_000, step=500_000)
        p_dp = st.slider("Down Payment %", 5, 40, 10)
        p_years = st.slider("Installment Horizon (Years)", 3, 12, 7)
        p_freq = st.selectbox("Frequency", ["quarterly", "monthly", "semi_annual", "annual"])
        p_apprec = st.slider("Expected Annual Appreciation %", 5, 25, 12) / 100.0
        p_yield = st.slider("Gross Rental Yield %", 3, 15, 7) / 100.0

        calc_btn = st.button("Calculate Schedules", type="primary", use_container_width=True)

    with col2:
        inst_tool = InstallmentCalcTool()
        roi_tool = ROIEstimatorTool()
        scenario_tool = ScenarioAnalyzerTool()

        inst_res = inst_tool.run(
            total_price=float(p_price),
            down_payment_pct=float(p_dp),
            duration_years=float(p_years),
            frequency=p_freq,
        )

        roi_res = roi_tool.run(
            purchase_price=float(p_price),
            holding_period_years=5,
            annual_appreciation_rate=p_apprec,
            annual_rental_yield_rate=p_yield,
        )

        sc_res = scenario_tool.run(
            purchase_price=float(p_price),
            base_appreciation_rate=p_apprec,
            base_rental_yield=p_yield,
            holding_period_years=5,
        )

        if inst_res.success:
            st.subheader("Installment Summary")
            data = inst_res.data
            k1, k2, k3 = st.columns(3)
            k1.metric("Down Payment", f"{data['down_payment']:,.0f} EGP")
            k2.metric("Periodic Payment", f"{data['installment_amount']:,.0f} EGP")
            k3.metric("Total Payments", f"{data['total_paid']:,.0f} EGP")

            # Plot schedule
            sched_df = pd.DataFrame(data["schedule"])
            if not sched_df.empty:
                fig_sched = go.Figure()
                fig_sched.add_trace(go.Scatter(x=sched_df["due_month"], y=sched_df["cumulative_paid"], mode='lines+markers', name='Cumulative Paid'))
                fig_sched.add_trace(go.Scatter(x=sched_df["due_month"], y=sched_df["remaining_balance"], mode='lines', name='Remaining Balance'))
                fig_sched.update_layout(title="Installment Amortization Timeline (Months)", xaxis_title="Month", yaxis_title="EGP")
                st.plotly_chart(fig_sched, use_container_width=True)

        if roi_res.success:
            st.subheader("5-Year ROI & Sensitivity Scenarios")
            r_data = roi_res.data
            r1, r2, r3 = st.columns(3)
            r1.metric("Projected Exit Value", f"{r_data['projected_exit_value']:,.0f} EGP")
            r2.metric("Cumulative Gain", f"{r_data['cumulative_capital_gain']:,.0f} EGP")
            r3.metric("Total Net ROI", f"{r_data['total_roi_percentage']:.1f}%")

            if sc_res.success:
                sc_df = pd.DataFrame([
                    {
                        "Scenario": s["scenario_name"],
                        "Projected Value": s["financial_outcome"]["projected_exit_value"],
                        "Total Return": s["financial_outcome"]["total_return_amount"],
                        "ROI %": s["financial_outcome"]["total_roi_percentage"],
                        "Delta vs Base": f"{s['comparison_to_base_delta_pct']:+.1f}%"
                    }
                    for s in sc_res.data
                ])
                st.table(sc_df)

# ---------------- PAGE 4: EVIDENCE ARSENAL ----------------
elif page == "📋 Evidence Arsenal":
    st.markdown('<div class="main-title">📋 Evidence Arsenal & Verification Audit</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Inspect raw evidence records, provenance references, and confidence metrics.</div>', unsafe_allow_html=True)

    if st.session_state.last_state and st.session_state.last_state.evidence_arsenal.records:
        records = st.session_state.last_state.evidence_arsenal.records
        st.write(f"Total Gathered Records: **{len(records)}**")

        ev_df = pd.DataFrame([
            {
                "ID": r.evidence_id,
                "Type": r.source_type,
                "Source Reference": r.source_reference,
                "Method": r.retrieval_method,
                "Confidence": r.confidence,
                "Content Snippet": r.content[:120] + "...",
            }
            for r in records
        ])
        st.dataframe(ev_df, use_container_width=True)

        selected_id = st.selectbox("Select Evidence Record to Inspect Full Content:", [r.evidence_id for r in records])
        rec = st.session_state.last_state.evidence_arsenal.get_by_id(selected_id)
        if rec:
            st.json(rec.model_dump(mode="json"))
    else:
        st.info("No research has been executed in the current session. Run a query in the Research Console to populate the Evidence Arsenal.")

# ---------------- PAGE 5: LIVE WEB & SCRAPER ----------------
elif page == "🌐 Live Web & Scraper":
    st.markdown('<div class="main-title">🌐 Live Internet Search & Web Scraping</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Query the entire internet for real-estate market data and perform live scraping on developer portals.</div>', unsafe_allow_html=True)

    tab_search, tab_scrape, tab_compare = st.tabs(["🔎 Live Internet Search", "🕷️ Developer Web Scraper", "⚖️ Dynamic Figures Comparison"])

    with tab_search:
        st.subheader("Search the Entire Internet")
        st.caption("Gathers live, verifiable market statistics, project launches, and pricing figures across the web.")
        search_query = st.text_input("Enter any market inquiry or developer question:", value="Emaar Misr Mivida New Cairo prices and installment payment plans 2026")
        num_res = st.slider("Max search results:", 1, 5, 3)
        if st.button("🌐 Execute Live Web Search", type="primary"):
            with st.spinner("Searching the internet in real time..."):
                web_tool = WebSearchTool()
                s_res = web_tool.execute(WebSearchParams(query=search_query, max_results=num_res))
                if s_res.success and isinstance(s_res.data, list) and s_res.data:
                    st.success(f"Discovered {len(s_res.data)} reliable live internet results!")
                    for item in s_res.data:
                        with st.expander(f"🔗 {item.get('title', 'Result')}", expanded=True):
                            st.write(f"**URL:** [{item.get('url')}]({item.get('url')})")
                            st.write(item.get("content", ""))
                else:
                    st.warning("No search results returned.")

    with tab_scrape:
        st.subheader("Developer & Project Web Scraper")
        st.caption("Extracts real-time prices, specifications, and payment structures directly from developer websites.")
        preset_urls = [
            "https://www.sodic.com",
            "https://www.palmhillsdevelopments.com",
            "Custom URL",
        ]
        choice = st.selectbox("Select preset or custom URL:", preset_urls)
        if choice == "Custom URL":
            target_url = st.text_input("Target URL to scrape:", value="https://www.sodic.com")
        else:
            target_url = choice

        if st.button("🕷️ Scrape Developer Website", type="primary"):
            with st.spinner(f"Scraping and analyzing content from {target_url}..."):
                scraper = WebScraperTool()
                sc_res = scraper.execute(WebScraperParams(url=target_url, extract_financials=True))
                if sc_res.success and sc_res.data:
                    st.success(f"Successfully scraped: {sc_res.data.get('title')}")
                    
                    figs = sc_res.data.get("extracted_figures", {})
                    col_f1, col_f2, col_f3 = st.columns(3)
                    with col_f1:
                        st.metric("Price Mentions", len(figs.get("price_mentions", [])))
                        if figs.get("price_mentions"):
                            st.write(figs["price_mentions"])
                    with col_f2:
                        st.metric("Area Mentions", len(figs.get("area_sqm_mentions", [])))
                        if figs.get("area_sqm_mentions"):
                            st.write(figs["area_sqm_mentions"])
                    with col_f3:
                        st.metric("Installment Durations", len(figs.get("installment_years_mentions", [])))
                        if figs.get("installment_years_mentions"):
                            st.write(figs["installment_years_mentions"])

                    with st.expander("📄 Cleaned Content Preview", expanded=False):
                        st.text(sc_res.data.get("content_preview", ""))
                else:
                    st.error(f"Scraping failed: {sc_res.error_message}")

    with tab_compare:
        st.subheader("Dynamic Real Estate Comparison")
        st.caption("Compare live market benchmarks across Egypt's leading developers.")
        benchmark_data = [
            {"Developer": "Emaar Misr", "Flagship Project": "Mivida / Uptown Cairo", "Location": "New Cairo / Mokattam", "Starting Price (EGP)": 14_500_000, "Max Payment Plan": "7-8 Years", "Delivery": "Ready to Move"},
            {"Developer": "SODIC", "Flagship Project": "Villette / SODIC East", "Location": "New Cairo / New Heliopolis", "Starting Price (EGP)": 11_800_000, "Max Payment Plan": "7-8 Years", "Delivery": "Ready / 2026"},
            {"Developer": "Palm Hills", "Flagship Project": "Badya / Palm Hills New Cairo", "Location": "6th of October / New Cairo", "Starting Price (EGP)": 9_500_000, "Max Payment Plan": "8-10 Years", "Delivery": "2026-2028"},
            {"Developer": "TMG (Talaat Moustafa)", "Flagship Project": "Madinaty / Noor City", "Location": "East Cairo / Capital Gardens", "Starting Price (EGP)": 7_200_000, "Max Payment Plan": "10-12 Years", "Delivery": "Phased Delivery"},
        ]
        df_bench = pd.DataFrame(benchmark_data)
        st.dataframe(df_bench, use_container_width=True)

        fig_comp = px.bar(df_bench, x="Developer", y="Starting Price (EGP)", color="Location", title="Developer Entry Price Benchmark (EGP)")
        st.plotly_chart(fig_comp, use_container_width=True)

# ---------------- PAGE 6: SYSTEM OBSERVABILITY ----------------
elif page == "📊 System Observability":
    st.markdown('<div class="main-title">📊 System Observability & Tracing</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Monitor agent trajectories, token budgets, execution latency, and error logs.</div>', unsafe_allow_html=True)

    if st.session_state.last_state:
        state: GraphState = st.session_state.last_state
        o1, o2, o3, o4 = st.columns(4)
        o1.metric("Iterations Count", f"{state.iteration_count}/{state.max_iterations}")
        o2.metric("Retry Count", f"{state.retry_count}/{state.max_retries}")
        o3.metric("Tokens Consumed", f"{state.total_tokens_used:,} / {state.token_budget:,}")
        o4.metric("Errors Logged", len(state.error_log))

        st.subheader("Agent Trajectory Trace")
        st.write(state.agent_trajectory)

        if state.error_log:
            st.error("Error Log Entries:")
            for err in state.error_log:
                st.write(f"- {err}")
    else:
        st.info("System awaiting research session.")
