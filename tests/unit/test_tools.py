import pytest
from src.tools.property_search import PropertySearchTool, PropertySearchParams
from src.tools.property_details import PropertyDetailsTool, PropertyDetailsParams
from src.tools.developer_lookup import DeveloperLookupTool, DeveloperLookupParams
from src.tools.installment_calc import InstallmentCalcTool, InstallmentCalcParams
from src.tools.rag_retriever import RAGRetrieverTool, RAGRetrieverParams
from src.tools.web_search import WebSearchTool, WebSearchParams
from src.tools.web_scraper import WebScraperTool, WebScraperParams
from src.tools.registry import default_registry

def test_property_search_tool():
    tool = PropertySearchTool()
    res = tool.execute(PropertySearchParams(location="New Cairo", max_results=3))
    assert res.success
    assert len(res.data) > 0
    assert len(res.evidence_records) > 0
    assert "New Cairo" in res.data[0]["location"]

def test_property_details_tool():
    tool = PropertyDetailsTool()
    res = tool.execute(PropertyDetailsParams(property_id="PROP_001"))
    assert res.success
    assert res.data["project_name"] == "Mivida"
    assert len(res.evidence_records) == 1

def test_developer_lookup_tool():
    tool = DeveloperLookupTool()
    res = tool.execute(DeveloperLookupParams(developer_name="SODIC"))
    assert res.success
    assert res.data["name"] == "SODIC"
    assert res.data["total_delivered_units"] > 10000

def test_installment_calc_tool():
    tool = InstallmentCalcTool()
    res = tool.execute(
        InstallmentCalcParams(
            total_price=8_000_000.0,
            down_payment_pct=10.0,
            duration_years=8.0,
            frequency="quarterly",
        )
    )
    assert res.success
    assert res.data["down_payment"] == 800_000.0
    assert res.data["number_of_installments"] == 32

def test_tool_registry_get_tool():
    tool = default_registry.get_tool("PropertySearchTool")
    assert tool.name == "PropertySearchTool"
    assert default_registry["PropertySearchTool"].name == "PropertySearchTool"

    with pytest.raises(KeyError):
        default_registry.get_tool("NonExistentTool")

def test_web_search_tool():
    tool = WebSearchTool()
    res = tool.execute(WebSearchParams(query="New Cairo real estate average price per sqm", max_results=2))
    assert res.success
    assert len(res.evidence_records) > 0
    assert res.evidence_records[0].source_type == "web_search"

def test_web_scraper_tool_schema_and_execution():
    tool = WebScraperTool()
    res = tool.execute(WebScraperParams(url="https://example.com", extract_financials=True))
    assert res.success
    assert "example" in res.data["url"].lower()
    assert len(res.evidence_records) == 1
    assert res.evidence_records[0].source_type == "web_scraping"


