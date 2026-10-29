from pathlib import Path
from typing import Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from config.settings import settings
from src.rag.embeddings import EmbeddingService

class ChromaVectorStore:
    """Manages the local Chroma vector store instance and collections."""

    def __init__(
        self,
        persist_dir: str | None = None,
        collection_name: str | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        self.embedding_service = embedding_service or EmbeddingService()

        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        """Embeds and upserts documents with metadata into the collection."""
        embeddings = self.embedding_service.embed_documents(documents)
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where_filter: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Queries the collection using semantic similarity and optional metadata filters."""
        query_embedding = self.embedding_service.embed_query(query_text)
        query_kwargs: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
        }
        if where_filter:
            query_kwargs["where"] = where_filter

        results = self.collection.query(**query_kwargs)
        return results

    def count(self) -> int:
        return self.collection.count()

    def reset(self) -> None:
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
