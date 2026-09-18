from typing import TypedDict


class AgentState(TypedDict, total=False):
    question: str
    selected_agents: list[str]
    results: list[dict]
    critique: dict
    final_answer: str
