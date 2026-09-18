from pathlib import Path

from app.retrieval.chunker import chunk_document
from app.retrieval.document_loader import load_document
from app.retrieval.vector_store import index_chunks


def main() -> None:
    document_path = Path("data/documents/sample.pdf")

    print(f"Loading: {document_path}")

    document = load_document(document_path)

    print("Chunking document...")
    chunks = chunk_document(document)

    print(f"Chunks created: {len(chunks)}")
    print("Indexing into Qdrant...")

    indexed = index_chunks(
        chunks=chunks,
        source=document_path.name,
    )

    print(f"\nINDEXING COMPLETE: {indexed} chunks")


if __name__ == "__main__":
    main()
