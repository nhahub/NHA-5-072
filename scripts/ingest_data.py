import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.rag.ingestion import IngestionPipeline
from src.rag.vectorstore import ChromaVectorStore

def main() -> None:
    print("=" * 60)
    print("Atlas AQAR: Starting RAG Data Ingestion")
    print("=" * 60)

    store = ChromaVectorStore()
    pipeline = IngestionPipeline(vectorstore=store)

    stats = pipeline.ingest_all()
    print(f"[+] Properties Ingested:    {stats['properties_ingested']}")
    print(f"[+] Developers Ingested:    {stats['developers_ingested']}")
    print(f"[+] Market Reports Ingested:{stats['market_reports_ingested']}")
    print(f"[+] Total Chunks in Chroma: {store.count()}")
    print("=" * 60)
    print("Ingestion Completed Successfully!")

if __name__ == "__main__":
    main()
