import re
from typing import Any
import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from src.tools.base import BaseTool, ToolResult
from src.models.evidence import EvidenceRecord

class WebScraperParams(BaseModel):
    url: str = Field(description="Target developer or project web page URL to scrape")
    extract_financials: bool = Field(default=True, description="Whether to extract real estate pricing and figures")
    max_chars: int = Field(default=4000, description="Maximum extracted text characters")

class WebScraperTool(BaseTool):
    name = "WebScraperTool"
    description = "Performs standard live web scraping on real-estate developer portals and project pages to harvest verified specs, prices, and payment plans."
    parameters_schema = WebScraperParams

    def execute(self, params: WebScraperParams) -> ToolResult:
        url = params.url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        }

        try:
            with httpx.Client(timeout=12.0, follow_redirects=True) as client:
                resp = client.get(url, headers=headers)

            if resp.status_code >= 400:
                return ToolResult(
                    success=False,
                    error_message=f"HTTP {resp.status_code} while scraping {url}",
                )

            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove irrelevant clutter tags
            for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "svg", "form"]):
                tag.decompose()

            page_title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled Page"

            # Extract clean paragraphs and headers
            text_blocks = []
            for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "span"]):
                txt = element.get_text(separator=" ", strip=True)
                if len(txt) > 20 and txt not in text_blocks:
                    text_blocks.append(txt)

            full_text = "\n".join(text_blocks)[:params.max_chars]

            extracted_figures: dict[str, Any] = {}
            if params.extract_financials:
                # Prices in EGP or Millions
                price_matches = re.findall(r"(\d{1,3}(?:[,\.]\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s*(?:million|m|egp|le|جنيه|جنية)", full_text, flags=re.IGNORECASE)
                if price_matches:
                    extracted_figures["price_mentions"] = price_matches[:5]

                # Areas in SQM
                area_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:sqm|sq\.m|m2|متر)", full_text, flags=re.IGNORECASE)
                if area_matches:
                    extracted_figures["area_sqm_mentions"] = area_matches[:5]

                # Installment durations
                inst_matches = re.findall(r"(\d+)\s*(?:years?|yrs?|سنوات|سنة)", full_text, flags=re.IGNORECASE)
                if inst_matches:
                    extracted_figures["installment_years_mentions"] = inst_matches[:3]

                # Down payment %
                dp_matches = re.findall(r"(\d+(?:\.\d+)?)\s*%\s*(?:down|مقدم)", full_text, flags=re.IGNORECASE)
                if dp_matches:
                    extracted_figures["down_payment_pct_mentions"] = dp_matches[:3]

            evidence = [
                EvidenceRecord(
                    evidence_id="E-SCRAPE-001",
                    task_id="T_WEB_SCRAPING",
                    source_type="web_scraping",
                    source_reference=url,
                    retrieval_method="live_http_scraper",
                    content=f"Title: {page_title} | Summary: {full_text[:600]}...",
                    metadata={
                        "url": url,
                        "title": page_title,
                        "figures": extracted_figures,
                    },
                    confidence=0.85,
                )
            ]

            return ToolResult(
                success=True,
                data={
                    "url": url,
                    "title": page_title,
                    "content_preview": full_text[:1000],
                    "extracted_figures": extracted_figures,
                },
                evidence_records=evidence,
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Scraping failed for {url}: {str(e)}",
            )
