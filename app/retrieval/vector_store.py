from pathlib import Path
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import get_settings
from app.retrieval.embeddings import embed_documents, embed_query

COLLECTION_NAME = "documents"


def get_qdrant_client() -> QdrantClient:
    settings = get_settings()

    path = Path(settings.qdrant_path)
    path.mkdir(parents=True, exist_ok=True)

    return QdrantClient(path=str(path))


def recreate_collection(vector_size: int) -> None:
    client = get_qdrant_client()

    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )


def index_chunks(chunks: list[str], source: str) -> int:
    if not chunks:
        return 0

    vectors = embed_documents(chunks)

    recreate_collection(len(vectors[0]))

    client = get_qdrant_client()

    points = []

    for index, (text, vector) in enumerate(
        zip(chunks, vectors, strict=True)
    ):
        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "text": text,
                    "source": source,
                    "chunk_index": index,
                },
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    return len(points)


def semantic_search(query: str, limit: int = 3) -> list[dict]:
    query_vector = embed_query(query)

    client = get_qdrant_client()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True,
    ).points

    return [
        {
            "score": result.score,
            "text": result.payload.get("text", ""),
            "source": result.payload.get("source", ""),
            "chunk_index": result.payload.get("chunk_index"),
        }
        for result in results
    ]
