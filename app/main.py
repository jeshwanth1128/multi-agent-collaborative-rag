from fastapi import FastAPI
from pydantic import BaseModel

from app.graph.workflow import workflow

app = FastAPI(
    title="Multi-Agent Collaborative RAG",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "project": "Multi-Agent Collaborative RAG",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/ask")
def ask(request: AskRequest):
    result = workflow.invoke(
        {
            "question": request.question
        }
    )

    return {
        "question": request.question,
        "agents": result.get(
            "selected_agents",
            [],
        ),
        "critique": result.get(
            "critique",
            {},
        ),
        "answer": result.get(
            "final_answer",
            "",
        ),
    }
