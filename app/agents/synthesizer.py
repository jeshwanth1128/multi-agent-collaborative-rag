def synthesize_answer(question: str, results: list[dict]) -> str:
    sections = []

    for result in results:
        agent = result.get("agent")
        evidence = result.get("results", [])

        if not evidence:
            continue

        if agent == "document":
            text = "\n\n".join(
                item.get("text", "")
                for item in evidence[:3]
            )

            sections.append(
                f"DOCUMENT EVIDENCE:\n{text}"
            )

        elif agent == "database":
            lines = [
                (
                    f"{item.get('product')} | "
                    f"{item.get('quarter')} | "
                    f"Revenue: {item.get('revenue')}"
                )
                for item in evidence
            ]

            sections.append(
                "DATABASE EVIDENCE:\n" + "\n".join(lines)
            )

        elif agent == "web":
            lines = [
                (
                    f"{item.get('title')}\n"
                    f"{item.get('snippet')}\n"
                    f"{item.get('url')}"
                )
                for item in evidence
            ]

            sections.append(
                "WEB EVIDENCE:\n" + "\n\n".join(lines)
            )

    if not sections:
        return "No sufficient evidence was found."

    return (
        f"Question: {question}\n\n"
        + "\n\n".join(sections)
    )
