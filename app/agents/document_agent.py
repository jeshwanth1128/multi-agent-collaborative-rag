from app.retrieval.vector_store import semantic_search


def run_document_agent(query: str, limit: int = 3) -> dict:
    results = semantic_search(query, limit=limit)

    return {
        "agent": "document",
        "query": query,
        "results": results,
    }
