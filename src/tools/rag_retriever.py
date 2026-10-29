from pydantic import BaseModel, Field
from src.tools.base import BaseTool, ToolResult
from src.rag.retriever import RAGRetriever

class RAGRetrieverParams(BaseModel):
    query: str = Field(description="Semantic inquiry or market question")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of document chunks to retrieve")
    doc_type: str | None = Field(default=None, description="Optional doc_type filter: property, developer, market_report")
    location: str | None = Field(default=None, description="Optional location filter")

class RAGRetrieverTool(BaseTool):
    name = "RAGRetrieverTool"
    description = "Retrieves evidence-grounded real estate knowledge, developer track records, and market research from Chroma vector store."
    parameters_schema = RAGRetrieverParams

    def __init__(self, retriever: RAGRetriever | None = None) -> None:
        self.retriever = retriever or RAGRetriever()

    def execute(self, params: RAGRetrieverParams) -> ToolResult:
        evidence = self.retriever.retrieve_as_evidence(
            query=params.query,
            top_k=params.top_k,
            doc_type=params.doc_type,
        )

        return ToolResult(
            success=True,
            data=[e.model_dump() for e in evidence],
            evidence_records=evidence,
        )
