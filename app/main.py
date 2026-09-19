import logging
import secrets
import sqlite3
from contextlib import asynccontextmanager, closing
from threading import BoundedSemaphore
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, StringConstraints

from app.agents.synthesizer import evidence_items
from app.config import get_settings
from app.graph.workflow import workflow
from app.retrieval.vector_store import close_qdrant_client, document_count

_capacity = BoundedSemaphore(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_qdrant_client()


app = FastAPI(title="Multi-Agent Collaborative RAG", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)


class AskRequest(BaseModel):
    question: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)
    ]


class AskResponse(BaseModel):
    question: str
    agents: list[str]
    critique: dict
    answer: str
    answer_mode: str
    evidence: list[dict]
    warnings: list[str] = Field(default_factory=list)


def authorize(x_api_key: str | None = Header(default=None)):
    settings = get_settings()
    expected = settings.backend_api_key.get_secret_value()
    if settings.environment == "production" and not expected:
        raise HTTPException(
            503, "The service requires production access configuration."
        )
    if expected and not secrets.compare_digest(expected, x_api_key or ""):
        raise HTTPException(401, "Unauthorized.")


@app.get("/")
def root():
    return {"project": "Multi-Agent Collaborative RAG", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/sources", dependencies=[Depends(authorize)])
def sources(response: Response):
    response.headers["Cache-Control"] = "no-store"
    status = {}
    try:
        count = document_count()
        status["document"] = {
            "status": "ready" if count else "empty",
            "detail": f"{count} indexed passages",
        }
    except Exception as exc:  # noqa: BLE001 -- readiness is independent per source
        logging.getLogger(__name__).warning(
            "Document readiness failed (%s)", type(exc).__name__
        )
        status["document"] = {
            "status": "unavailable",
            "detail": "Document index unavailable",
        }
    settings = get_settings()
    path = settings.resolve_path(settings.database_path)
    try:
        with closing(
            sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True, timeout=5)
        ) as connection:
            count = connection.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        status["database"] = {
            "status": "ready" if count else "empty",
            "detail": f"{count} sales records",
        }
    except sqlite3.Error:
        status["database"] = {
            "status": "unavailable",
            "detail": "Sales database unavailable",
        }
    status["web"] = {
        "status": "available" if settings.web_search_enabled else "disabled",
        "detail": "Searched on request"
        if settings.web_search_enabled
        else "Disabled in configuration",
    }
    return {"sources": status}


@app.post("/ask", response_model=AskResponse, dependencies=[Depends(authorize)])
def ask(request: AskRequest, response: Response):
    response.headers["Cache-Control"] = "no-store"
    if not _capacity.acquire(blocking=False):
        raise HTTPException(
            429,
            "The workspace is busy. Please try again shortly.",
            headers={"Retry-After": "10"},
        )
    try:
        result = workflow.invoke({"question": request.question})
        warnings = [
            item["error"] for item in result.get("results", []) if item.get("error")
        ]
        if result.get("synthesis_warning"):
            warnings.append(result["synthesis_warning"])
        return {
            "question": request.question,
            "agents": result.get("selected_agents", []),
            "critique": result.get("critique", {}),
            "answer": result.get("final_answer", ""),
            "answer_mode": result.get("answer_mode", "evidence"),
            "evidence": evidence_items(result.get("results", [])),
            "warnings": warnings,
        }
    except Exception as exc:  # noqa: BLE001 -- return a safe error without leaking provider details
        logging.getLogger(__name__).error("Query failed (%s)", type(exc).__name__)
        raise HTTPException(
            503, "The query could not be completed. Please retry."
        ) from None
    finally:
        _capacity.release()
