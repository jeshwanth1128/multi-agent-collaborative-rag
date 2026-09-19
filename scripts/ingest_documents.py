import argparse
from pathlib import Path

from app.config import PROJECT_ROOT
from app.retrieval.chunker import chunk_document
from app.retrieval.document_loader import load_document
from app.retrieval.vector_store import index_chunks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Index a document without deleting other sources."
    )
    parser.add_argument(
        "path", nargs="?", default=str(PROJECT_ROOT / "data/documents/sample.pdf")
    )
    document_path = Path(parser.parse_args().path).resolve()

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
