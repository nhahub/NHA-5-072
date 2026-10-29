from typing import Any
from pydantic import BaseModel, Field
from src.rag.vectorstore import ChromaVectorStore
from src.models.evidence import EvidenceRecord

class RetrievedChunk(BaseModel):
    chunk_id: str
    content: str
    metadata: dict[str, Any]
    score: float

class RAGRetriever:
    """Retrieves grounded document chunks with metadata filtering and relevance scoring."""

    def __init__(self, vectorstore: ChromaVectorStore | None = None) -> None:
        self.vectorstore = vectorstore or ChromaVectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        doc_type: str | None = None,
        location: str | None = None,
        min_score: float = 0.0,
    ) -> list[RetrievedChunk]:
        where_filter: dict[str, Any] = {}
        if doc_type and location:
            where_filter = {"$and": [{"doc_type": doc_type}, {"location": location}]}
        elif doc_type:
            where_filter = {"doc_type": doc_type}
        elif location:
            where_filter = {"location": location}

        results = self.vectorstore.query(
            query_text=query,
            n_results=top_k,
            where_filter=where_filter if where_filter else None,
        )

        chunks: list[RetrievedChunk] = []
        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0] if "distances" in results else [0.0] * len(ids)

        for i, doc_id in enumerate(ids):
            # Cosine distance in Chroma: score = 1 - distance
            dist = distances[i] if i < len(distances) else 0.0
            similarity = round(max(0.0, min(1.0, 1.0 - dist)), 4)
            if similarity >= min_score:
                chunks.append(
                    RetrievedChunk(
                        chunk_id=doc_id,
                        content=docs[i],
                        metadata=metas[i] if i < len(metas) else {},
                        score=similarity,
                    )
                )

        return chunks

    def retrieve_as_evidence(
        self,
        query: str,
        task_id: str = "T_RAG_RETRIEVE",
        top_k: int = 3,
        doc_type: str | None = None,
    ) -> list[EvidenceRecord]:
        chunks = self.retrieve(query=query, top_k=top_k, doc_type=doc_type)
        evidence_list: list[EvidenceRecord] = []
        for i, c in enumerate(chunks):
            evidence_list.append(
                EvidenceRecord(
                    evidence_id=f"E-RAG-{i+1:03d}",
                    task_id=task_id,
                    source_type="rag_retrieval",
                    source_reference=f"ChromaDB::{c.chunk_id}",
                    retrieval_method="semantic_cosine_similarity",
                    content=c.content,
                    metadata=c.metadata,
                    confidence=c.score or 0.85,
                )
            )
        return evidence_list
