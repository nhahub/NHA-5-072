import json
from pathlib import Path
from typing import Any
from config.settings import settings
from src.rag.vectorstore import ChromaVectorStore

class IngestionPipeline:
    """Ingests raw property, developer, and market report datasets into the Chroma vector store."""

    def __init__(self, vectorstore: ChromaVectorStore | None = None) -> None:
        self.vectorstore = vectorstore or ChromaVectorStore()

    def ingest_all(self, raw_dir: Path | None = None) -> dict[str, int]:
        target_dir = raw_dir or settings.RAW_DATA_DIR
        stats = {
            "properties_ingested": self.ingest_properties(target_dir / "properties.json"),
            "developers_ingested": self.ingest_developers(target_dir / "developers.json"),
            "market_reports_ingested": self.ingest_market_reports(target_dir / "market_reports.json"),
        }
        return stats

    def ingest_properties(self, filepath: Path) -> int:
        if not filepath.exists():
            return 0
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        ids, docs, metas = [], [], []
        for p in data:
            doc_id = f"doc_prop_{p['property_id']}"
            content = (
                f"Project: {p['project_name']} | Developer: {p['developer_name']} | Type: {p['property_type']} | "
                f"Location: {p['location']} ({p.get('sub_location') or 'Central'}) | Area: {p['area_sqm']} sqm | "
                f"Bedrooms: {p.get('bedrooms')} | Price: {p['price']:,.0f} EGP | "
                f"Price/sqm: {p['price_per_sqm']:,.0f} EGP | Delivery: {p.get('delivery_date')} | "
                f"Description: {p.get('description', '')} | Amenities: {', '.join(p.get('amenities', []))}."
            )
            meta = {
                "doc_type": "property",
                "property_id": str(p["property_id"]),
                "project_name": str(p["project_name"]),
                "developer_name": str(p["developer_name"]),
                "location": str(p["location"]),
                "property_type": str(p["property_type"]),
                "price": float(p["price"]),
                "area_sqm": float(p["area_sqm"]),
                "bedrooms": int(p.get("bedrooms") or 0),
            }
            ids.append(doc_id)
            docs.append(content)
            metas.append(meta)

        if ids:
            self.vectorstore.add_documents(ids, docs, metas)
        return len(ids)

    def ingest_developers(self, filepath: Path) -> int:
        if not filepath.exists():
            return 0
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        ids, docs, metas = [], [], []
        for d in data:
            doc_id = f"doc_dev_{d['developer_id']}"
            content = (
                f"Developer: {d['name']} | Established: {d.get('established_year')} | HQ: {d.get('headquarters')} | "
                f"Total Delivered Units: {d.get('total_delivered_units')} | Rating: {d.get('financial_solvency_rating')} | "
                f"Notable Projects: {', '.join(d.get('notable_projects', []))} | "
                f"Reputation & Track Record: {d.get('reputation_notes')}."
            )
            meta = {
                "doc_type": "developer",
                "developer_id": str(d["developer_id"]),
                "developer_name": str(d["name"]),
                "rating": str(d.get("financial_solvency_rating") or "N/A"),
            }
            ids.append(doc_id)
            docs.append(content)
            metas.append(meta)

        if ids:
            self.vectorstore.add_documents(ids, docs, metas)
        return len(ids)

    def ingest_market_reports(self, filepath: Path) -> int:
        if not filepath.exists():
            return 0
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        ids, docs, metas = [], [], []
        for r in data:
            doc_id = f"doc_mkt_{r['report_id']}"
            content = (
                f"Title: {r['title']} | Region: {r['region']} | Date: {r['publication_date']} | "
                f"Source: {r['source']} | Summary: {r.get('summary', '')} | Content: {r['content']}"
            )
            meta = {
                "doc_type": "market_report",
                "report_id": str(r["report_id"]),
                "region": str(r["region"]),
                "publication_date": str(r["publication_date"]),
                "source": str(r["source"]),
            }
            ids.append(doc_id)
            docs.append(content)
            metas.append(meta)

        if ids:
            self.vectorstore.add_documents(ids, docs, metas)
        return len(ids)
