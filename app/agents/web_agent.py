import logging
from urllib.parse import urlsplit

from ddgs import DDGS

from app.config import get_settings


def run_web_agent(query: str, limit: int = 3) -> dict:
    if not get_settings().web_search_enabled:
        return {"agent": "web", "results": [], "error": "Web search is disabled."}
    try:
        results = DDGS(timeout=12).text(query, max_results=limit)
        cleaned = [
            {
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "snippet": item.get("body", ""),
            }
            for item in results
            if urlsplit(item.get("href", "")).scheme in {"http", "https"}
        ]
        return {"agent": "web", "query": query, "results": cleaned}
    except Exception as exc:  # noqa: BLE001 -- external search may fail independently
        logging.getLogger(__name__).warning(
            "Web search failed (%s)", type(exc).__name__
        )
        return {
            "agent": "web",
            "query": query,
            "results": [],
            "error": "Web search is temporarily unavailable. Please retry.",
        }
