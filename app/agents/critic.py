def evaluate_results(results: list[dict]) -> dict:
    successful_agents = []
    failed_agents = []

    for result in results:
        agent = result.get("agent", "unknown")
        evidence = result.get("results", [])

        if evidence:
            successful_agents.append(agent)
        else:
            failed_agents.append(agent)

    return {
        "passed": len(successful_agents) > 0,
        "successful_agents": successful_agents,
        "failed_agents": failed_agents,
    }
