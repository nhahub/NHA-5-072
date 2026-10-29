from typing import Any
from src.tools.base import BaseTool

class ToolRegistry:
    """Central registry for discovering, registering, and dispatching tools."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def get_tool(self, name: str) -> BaseTool:
        """Returns a registered tool by name; raises KeyError if not found."""
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"Tool '{name}' is not registered in ToolRegistry.")
        return tool

    def __getitem__(self, name: str) -> BaseTool:
        return self.get_tool(name)

    def list_tools(self) -> list[dict[str, Any]]:
        """Returns metadata description of registered tools for LLM agent selection."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters_schema": tool.parameters_schema.model_json_schema(),
            }
            for tool in self._tools.values()
        ]

    def get_all(self) -> dict[str, BaseTool]:
        return dict(self._tools)

    def get_for_task_type(self, task_type: str) -> list[BaseTool]:
        mapping = {
            "property_search": ["PropertySearchTool", "WebSearchTool", "RAGRetrieverTool"],
            "property_details": ["PropertyDetailsTool", "DeveloperLookupTool", "WebScraperTool"],
            "developer_research": ["DeveloperLookupTool", "WebScraperTool", "WebSearchTool", "RAGRetrieverTool"],
            "financial_analysis": ["InstallmentCalcTool", "ROIEstimatorTool", "ScenarioAnalyzerTool"],
            "market_research": ["WebSearchTool", "WebScraperTool", "RAGRetrieverTool"],
            "comparison": ["PropertySearchTool", "PropertyDetailsTool", "InstallmentCalcTool", "WebSearchTool"],
            "scenario_analysis": ["ScenarioAnalyzerTool", "ROIEstimatorTool"],
            "web_scraping": ["WebScraperTool", "WebSearchTool"],
            "general_research": ["WebSearchTool", "WebScraperTool", "RAGRetrieverTool"],
        }
        tool_names = mapping.get(task_type, list(self._tools.keys()))
        return [self._tools[name] for name in tool_names if name in self._tools]

default_registry = ToolRegistry()
