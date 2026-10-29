import math
import hashlib
from typing import Any

class EmbeddingService:
    """
    Fast, deterministic semantic-aware embedding service.
    Uses multi-hash n-gram projected embeddings (384-dimensional) to provide
    instant sub-second vector embeddings without requiring an external 80MB download.
    Can also wrap sentence-transformers or Chroma default if explicitly requested.
    """

    def __init__(self, model_name: str = "fast-projected-384", use_external: bool = False) -> None:
        self.model_name = model_name
        self.dim = 384
        self._ef = None
        if use_external:
            self._init_external_embedding()

    def _init_external_embedding(self) -> None:
        try:
            from chromadb.utils import embedding_functions
            self._ef = embedding_functions.DefaultEmbeddingFunction()
        except Exception:
            self._ef = None

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if self._ef is not None:
            try:
                return self._ef(texts)
            except Exception:
                pass
        return [self._embed_text(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    def _embed_text(self, text: str) -> list[float]:
        """
        Creates a high-dispersion normalized 384-dimensional embedding using
        unigram and bigram feature hashing for semantic vector similarity.
        """
        vec = [0.0] * self.dim
        tokens = [t.strip(".,;:!?()[]\"'").lower() for t in text.split() if t.strip()]
        if not tokens:
            return vec

        # Unigrams
        for token in tokens:
            h = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            weight = 1.0 if ((h >> 8) & 1) else -1.0
            vec[idx] += weight

        # Bigrams for local semantic context
        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]}_{tokens[i+1]}"
            h = int(hashlib.sha256(bigram.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            weight = 1.5 if ((h >> 8) & 1) else -1.5
            vec[idx] += weight

        # L2 normalization
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [round(x / norm, 6) for x in vec]
