from src.tools.base import BaseTool, ToolResult
from src.tools.registry import ToolRegistry, default_registry
from src.tools.property_search import PropertySearchTool
from src.tools.property_details import PropertyDetailsTool
from src.tools.developer_lookup import DeveloperLookupTool
from src.tools.installment_calc import InstallmentCalcTool
from src.tools.roi_estimator import ROIEstimatorTool
from src.tools.scenario_analyzer import ScenarioAnalyzerTool
from src.tools.rag_retriever import RAGRetrieverTool
from src.tools.web_search import WebSearchTool
from src.tools.web_scraper import WebScraperTool

# Register all tools into default_registry
default_registry.register(PropertySearchTool())
default_registry.register(PropertyDetailsTool())
default_registry.register(DeveloperLookupTool())
default_registry.register(InstallmentCalcTool())
default_registry.register(ROIEstimatorTool())
default_registry.register(ScenarioAnalyzerTool())
default_registry.register(RAGRetrieverTool())
default_registry.register(WebSearchTool())
default_registry.register(WebScraperTool())

__all__ = [
    "BaseTool",
    "ToolResult",
    "ToolRegistry",
    "default_registry",
    "PropertySearchTool",
    "PropertyDetailsTool",
    "DeveloperLookupTool",
    "InstallmentCalcTool",
    "ROIEstimatorTool",
    "ScenarioAnalyzerTool",
    "RAGRetrieverTool",
    "WebSearchTool",
    "WebScraperTool",
]
