from langgraph.graph import END, START, StateGraph

from app.agents.critic import evaluate_results
from app.agents.database_agent import run_database_agent
from app.agents.document_agent import run_document_agent
from app.agents.synthesizer import synthesize_answer
from app.agents.web_agent import run_web_agent
from app.graph.routing import route_query
from app.graph.state import AgentState


def router_node(state: AgentState):
    return {
        "selected_agents": route_query(
            state["question"]
        )
    }


def agents_node(state: AgentState):
    question = state["question"]
    selected = state["selected_agents"]

    results = []

    for agent in selected:
        if agent == "document":
            results.append(
                run_document_agent(question)
            )

        elif agent == "database":
            results.append(
                run_database_agent(question)
            )

        elif agent == "web":
            results.append(
                run_web_agent(question)
            )

    return {
        "results": results
    }


def critic_node(state: AgentState):
    return {
        "critique": evaluate_results(
            state["results"]
        )
    }


def synthesis_node(state: AgentState):
    return {
        "final_answer": synthesize_answer(
            state["question"],
            state["results"],
        )
    }


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
