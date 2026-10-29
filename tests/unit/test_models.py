import pytest
from src.models.evidence import EvidenceRecord, EvidenceArsenal
from src.models.property import PropertyListing, PaymentPlan
from src.models.financial import InstallmentSchedule, ROIResult
from src.models.research import ResearchTask, ResearchPlan
from src.models.state import GraphState, WorkflowPhase

def test_evidence_arsenal_auto_indexing():
    arsenal = EvidenceArsenal()
    r1 = EvidenceRecord(
        evidence_id="",
        task_id="T01",
        source_type="property_tool",
        source_reference="test_ref",
        content="Test content 1",
    )
    arsenal.add(r1)
    assert r1.evidence_id == "E001"
    assert arsenal.get_by_id("E001") is not None
    assert len(arsenal.get_by_task("T01")) == 1

def test_property_listing_validation():
    prop = PropertyListing(
        property_id="P01",
        project_name="Test Project",
        developer_name="Test Dev",
        property_type="apartment",
        location="New Cairo",
        area_sqm=150.0,
        price=10_000_000.0,
        price_per_sqm=66_666.67,
    )
    assert prop.area_sqm == 150.0
    assert prop.price == 10_000_000.0

def test_graph_state_defaults():
    state = GraphState(user_query="Search for villas in Zayed")
    assert state.phase == WorkflowPhase.PLANNING
    assert state.iteration_count == 0
    assert state.retry_count == 0
    assert len(state.evidence_arsenal.records) == 0
