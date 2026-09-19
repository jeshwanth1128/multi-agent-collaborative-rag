from functools import lru_cache
from threading import RLock
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    HasIdCondition,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.config import get_settings
from app.retrieval.embeddings import embed_documents, embed_query

COLLECTION_NAME = "documents"
_lock = RLock()


@lru_cache(maxsize=1)
def _create_client() -> QdrantClient:
    settings = get_settings()
    if settings.qdrant_url:
        return QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key.get_secret_value() or None,
            timeout=15,
        )
    path = settings.resolve_path(settings.qdrant_path)
    path.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(path), force_disable_check_same_thread=True)


def get_qdrant_client() -> QdrantClient:
    # Embedded storage permits only one client per process.
    with _lock:
        return _create_client()


def close_qdrant_client() -> None:
    with _lock:
        if _create_client.cache_info().currsize:
            _create_client().close()
            _create_client.cache_clear()


def document_count() -> int:
    with _lock:
        client = get_qdrant_client()
        if not client.collection_exists(COLLECTION_NAME):
            return 0
        return client.count(COLLECTION_NAME, exact=True).count


def index_chunks(chunks: list[str], source: str) -> int:
    if not chunks:
        return 0
    vectors = embed_documents(chunks)
    points = [
        PointStruct(
            id=str(uuid5(NAMESPACE_URL, f"{source}:{index}")),
            vector=vector,
            payload={"text": text, "source": source, "chunk_index": index},
        )
        for index, (text, vector) in enumerate(zip(chunks, vectors, strict=True))
    ]
    with _lock:
        client = get_qdrant_client()
        if not client.collection_exists(COLLECTION_NAME):
            client.create_collection(
                COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=len(vectors[0]), distance=Distance.COSINE
                ),
            )
        # Upload first so a failed embedding/upload does not erase existing evidence.
        client.upsert(COLLECTION_NAME, points=points, wait=True)
        client.delete(
            COLLECTION_NAME,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[FieldCondition(key="source", match=MatchValue(value=source))],
                    must_not=[HasIdCondition(has_id=[point.id for point in points])],
                )
            ),
            wait=True,
        )
    return len(points)


def semantic_search(query: str, limit: int = 3) -> list[dict]:
    if not document_count():
        return []
    query_vector = embed_query(query)
    with _lock:
        results = (
            get_qdrant_client()
            .query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                limit=limit,
                with_payload=True,
            )
            .points
        )
    return [
        {
            "score": result.score,
            "text": (result.payload or {}).get("text", ""),
            "source": (result.payload or {}).get("source", ""),
            "chunk_index": (result.payload or {}).get("chunk_index"),
        }
        for result in results
    ]
