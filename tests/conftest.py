import sys
from pathlib import Path
import pytest

# Ensure root directory is on PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.models.evidence import EvidenceArsenal, EvidenceRecord
from src.models.property import PropertyListing
from src.models.research import UserPreferences

@pytest.fixture
def sample_arsenal() -> EvidenceArsenal:
    arsenal = EvidenceArsenal()
    arsenal.add(
        EvidenceRecord(
            evidence_id="E001",
            task_id="T01",
            source_type="property_tool",
            source_reference="properties.json#PROP_001",
            content="Mivida by Emaar Misr in New Cairo: 170 sqm apartment, 14,500,000 EGP.",
        )
    )
    arsenal.add(
        EvidenceRecord(
            evidence_id="E101",
            task_id="T03",
            source_type="developer_tool",
            source_reference="developers.json#DEV_001",
            content="Emaar Misr is a Tier-1 developer with over 25,000 delivered units in Egypt.",
        )
    )
    return arsenal

@pytest.fixture
def sample_preferences() -> UserPreferences:
    return UserPreferences(
        budget_max=15_000_000,
        preferred_locations=["New Cairo"],
        min_bedrooms=3,
        holding_period_years=5,
    )
