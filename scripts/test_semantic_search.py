from app.retrieval.vector_store import semantic_search


def main() -> None:
    query = "What AI and machine learning skills does this candidate have?"

    results = semantic_search(query, limit=3)

    print(f"\nQUERY: {query}\n")

    for index, result in enumerate(results, start=1):
        print(f"--- RESULT {index} ---")
        print(f"Score: {result['score']:.4f}")
        print(f"Source: {result['source']}")
        print(result["text"])
        print()


if __name__ == "__main__":
    main()
