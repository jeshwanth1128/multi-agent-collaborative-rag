from app.retrieval.chunker import chunk_document
from app.retrieval.document_loader import load_document


def main() -> None:
    document = load_document("data/documents/sample.pdf")

    chunks = chunk_document(document)

    print(f"\nTOTAL CHUNKS: {len(chunks)}\n")

    for index, chunk in enumerate(chunks[:5], start=1):
        print(f"--- CHUNK {index} ---")
        print(chunk[:1000])
        print()


if __name__ == "__main__":
    main()
