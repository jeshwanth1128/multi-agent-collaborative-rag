from ddgs import DDGS


def run_web_agent(query: str, limit: int = 3) -> dict:
    try:
        results = DDGS().text(
            query,
            max_results=limit,
        )

        cleaned = [
            {
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "snippet": item.get("body", ""),
            }
            for item in results
        ]

        return {
            "agent": "web",
            "query": query,
            "results": cleaned,
        }

    except Exception as exc:
        return {
            "agent": "web",
            "query": query,
            "results": [],
            "error": str(exc),
        }
