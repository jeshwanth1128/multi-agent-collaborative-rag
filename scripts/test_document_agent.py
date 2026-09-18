from app.agents.document_agent import run_document_agent


def main() -> None:
    result = run_document_agent(
        "What AI skills does this candidate have?"
    )

    print("\nDOCUMENT AGENT RESULT\n")

    for item in result["results"]:
        print(f"Score: {item['score']:.4f}")
        print(item["text"])
        print()


if __name__ == "__main__":
    main()
