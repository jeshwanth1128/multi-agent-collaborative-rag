def route_query(question: str) -> list[str]:
    text = question.lower()

    agents = []

    document_words = [
        "resume",
        "candidate",
        "document",
        "pdf",
        "report",
        "skills",
        "strategy",
        "policy",
    ]

    database_words = [
        "database",
        "sales",
        "revenue",
        "product",
        "q3",
        "q2",
        "q1",
        "q4",
        "transaction",
    ]

    web_words = [
        "web",
        "online",
        "current",
        "latest",
        "today",
        "market",
        "internet",
    ]

    if any(word in text for word in document_words):
        agents.append("document")

    if any(word in text for word in database_words):
        agents.append("database")

    if any(word in text for word in web_words):
        agents.append("web")

    if not agents:
        agents.append("document")

    return agents
