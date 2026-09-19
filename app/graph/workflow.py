import logging

from langgraph.graph import END, START, StateGraph

from app.agents.critic import evaluate_results
from app.agents.database_agent import run_database_agent
from app.agents.document_agent import run_document_agent
from app.agents.synthesizer import synthesize_response
from app.agents.web_agent import run_web_agent
from app.graph.routing import route_query
from app.graph.state import AgentState


def router_node(state: AgentState):
    return {"selected_agents": route_query(state["question"])}


def agents_node(state: AgentState):
    runners = {
        "document": run_document_agent,
        "database": run_database_agent,
        "web": run_web_agent,
    }
    results = []
    for agent in state["selected_agents"]:
        try:
            results.append(runners[agent](state["question"]))
        except Exception as exc:  # noqa: BLE001 -- isolate provider failures; preserve other evidence
            logging.getLogger(__name__).warning(
                "%s retrieval failed (%s)", agent, type(exc).__name__
            )
            results.append(
                {
                    "agent": agent,
                    "results": [],
                    "error": f"The {agent} source is temporarily unavailable.",
                }
            )
    return {"results": results}


def critic_node(state: AgentState):
    return {"critique": evaluate_results(state["results"])}


def synthesis_node(state: AgentState):
    return synthesize_response(state["question"], state["results"])


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("router", router_node)
    graph.add_node("agents", agents_node)
    graph.add_node("critic", critic_node)
    graph.add_node("synthesis", synthesis_node)
    graph.add_edge(START, "router")
    graph.add_edge("router", "agents")
    graph.add_edge("agents", "critic")
    graph.add_edge("critic", "synthesis")
    graph.add_edge("synthesis", END)
    return graph.compile()


workflow = build_graph()
