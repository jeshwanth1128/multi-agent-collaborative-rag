from functools import lru_cache

from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_documents(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    model = get_embedding_model()

    vector = model.encode(
        text,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return vector.tolist()
