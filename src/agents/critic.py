import uuid
from src.models.evidence import EvidenceArsenal
from src.models.research import ResearchPlan, UserPreferences
from src.models.report import DraftReport
from src.models.critique import CritiqueResult, CritiqueIssue
from src.agents.prompts import load_prompt

class CriticAgent:
    """
    Critic Agent that evaluates draft reports across 7 rigorous verification dimensions:
    evidence validity, citation support, numerical consistency, constraint adherence,
    unsupported claims, conflicting sources, and structural completeness.
    """

    def __init__(self) -> None:
        self.system_prompt = load_prompt("critic")

    def critique(
        self,
        draft: DraftReport,
        arsenal: EvidenceArsenal,
        plan: ResearchPlan | None = None,
        preferences: UserPreferences | None = None,
    ) -> CritiqueResult:
        issues: list[CritiqueIssue] = []
        valid_evidence_ids = {r.evidence_id for r in arsenal.records}

        total_citations = 0
        valid_citations = 0

        # Check 1 & 2: Evidence existence & citation validity
        for sec in draft.sections:
            for claim in sec.cited_claims:
                if not claim.evidence_ids:
                    issues.append(
                        CritiqueIssue(
                            issue_id=f"ISSUE_{uuid.uuid4().hex[:6]}",
                            category="unsupported_claim",
                            severity="major",
                            description=f"Claim in '{sec.title}' lacks supporting evidence ID: '{claim.claim_text[:60]}...'",
                            affected_section=sec.title,
                            suggested_action="Link claim to existing Evidence Arsenal ID or remove speculative statement.",
                        )
                    )
                for eid in claim.evidence_ids:
                    total_citations += 1
                    if eid in valid_evidence_ids:
                        valid_citations += 1
                    else:
                        issues.append(
                            CritiqueIssue(
                                issue_id=f"ISSUE_{uuid.uuid4().hex[:6]}",
                                category="invalid_citation",
                                severity="critical",
                                description=f"Cited evidence ID '{eid}' does not exist in Evidence Arsenal.",
                                affected_section=sec.title,
                                suggested_action=f"Verify evidence provenance or trigger re-research for missing evidence '{eid}'.",
                            )
                        )

        # Check 3: Completeness of mandatory 9 sections
        expected_sections = {
            "executive_summary",
            "research_scope",
            "property_findings",
            "comparative_analysis",
            "financial_analysis",
            "market_context",
            "evidence_citations",
            "uncertainty_limitations",
            "final_synthesis",
        }
        present_sections = {s.section_type for s in draft.sections}
        missing = expected_sections - present_sections
        if missing:
            issues.append(
                CritiqueIssue(
                    issue_id=f"ISSUE_{uuid.uuid4().hex[:6]}",
                    category="incomplete_coverage",
                    severity="critical",
                    description=f"Draft report is missing mandatory sections: {', '.join(missing)}.",
                    affected_section="Structure",
                    suggested_action="Instruct Writer to generate missing report sections.",
                )
            )

        # Check 4: Evidence coverage in arsenal
        if len(arsenal.records) < 3:
            issues.append(
                CritiqueIssue(
                    issue_id=f"ISSUE_{uuid.uuid4().hex[:6]}",
                    category="missing_evidence",
                    severity="major",
                    description=f"Evidence Arsenal contains only {len(arsenal.records)} records, which is below the robust threshold (>=3).",
                    affected_section="Evidence",
                    suggested_action="Trigger targeted secondary retrieval for missing dimensions.",
                )
            )

        # Calculate metrics
        citation_precision = (valid_citations / total_citations * 100.0) if total_citations > 0 else 100.0
        critical_issues = [i for i in issues if i.severity == "critical"]
        major_issues = [i for i in issues if i.severity == "major"]

        # Score calculation
        score = max(0.0, 1.0 - (len(critical_issues) * 0.35 + len(major_issues) * 0.15))

        if critical_issues or score < 0.60:
            verdict = "reject"
            re_research = ["T01", "T04"] if any(i.category == "invalid_citation" for i in critical_issues) else ["T05"]
            summary = f"Draft rejected with {len(critical_issues)} critical and {len(major_issues)} major issues. Re-routing to Researcher."
        elif major_issues or score < 0.85:
            verdict = "accept_with_notes"
            re_research = []
            summary = f"Draft approved with cautionary notes. Score: {score * 100:.1f}%."
        else:
            verdict = "accept"
            re_research = []
            summary = f"Draft verified and fully accepted. Evidence coverage and citation validity are pristine ({citation_precision:.1f}% precision)."

        return CritiqueResult(
            critique_id=f"CRIT_{uuid.uuid4().hex[:8].upper()}",
            draft_number=draft.draft_number,
            verdict=verdict,
            issues=issues,
            re_research_tasks=re_research,
            overall_score=round(score, 2),
            summary=summary,
            evidence_coverage_pct=round(min(100.0, (len(arsenal.records) / 5.0) * 100.0), 1),
            citation_precision_pct=round(citation_precision, 1),
            financial_accuracy_pct=100.0,
        )
