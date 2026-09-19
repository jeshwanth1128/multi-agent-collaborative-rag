import sqlite3
from contextlib import closing

import pytest
from fastapi.testclient import TestClient
from qdrant_client import QdrantClient

from app.agents.database_agent import run_database_agent
from app.config import Settings
from app.graph.routing import route_query
from app.graph.workflow import agents_node
from app.main import app
from app.retrieval import vector_store


@pytest.fixture(autouse=True)
def settings(monkeypatch, tmp_path):
    config = Settings(
        _env_file=None,
        synthesis_enabled=False,
        database_path=str(tmp_path / "sales.db"),
        backend_api_key="",
        environment="development",
    )
    monkeypatch.setattr("app.main.get_settings", lambda: config)
    monkeypatch.setattr("app.agents.database_agent.get_settings", lambda: config)
    monkeypatch.setattr("app.agents.synthesizer.get_settings", lambda: config)
    return config


@pytest.fixture
def sales(settings):
    with closing(sqlite3.connect(settings.database_path)) as db:
        db.execute("CREATE TABLE sales (product TEXT, quarter TEXT, revenue REAL)")
        db.executemany(
            "INSERT INTO sales VALUES (?, ?, ?)",
            [("Q2 winner", "Q2", 999), ("Q3 winner", "Q3", 80), ("Other", "Q3", 20)],
        )
        db.commit()


def test_highest_respects_quarter(sales):
    rows = run_database_agent("Highest selling product in Q3")["results"]
    assert rows == [{"product": "Q3 winner", "quarter": "Q3", "revenue": 80}]


def test_total_respects_quarter(sales):
    assert run_database_agent("Total revenue in Q3")["results"][0]["revenue"] == 100


def test_missing_database_not_created(settings):
    from pathlib import Path

    assert run_database_agent("sales")["error"]
    assert not Path(settings.database_path).exists()


@pytest.mark.parametrize("question", ["", "   ", "x" * 2001, None, 42])
def test_invalid_questions(question):
    assert TestClient(app).post("/ask", json={"question": question}).status_code == 422


def test_local_frontend_cors_preflight():
    response = TestClient(app).options(
        "/ask",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_production_requires_auth(settings):
    settings.environment = "production"
    assert TestClient(app).get("/sources").status_code == 503
    from pydantic import SecretStr

    settings.backend_api_key = SecretStr("configured")
    assert TestClient(app).post("/ask", json={"question": "sales"}).status_code == 401


def test_end_to_end_database(sales):
    response = TestClient(app).post(
        "/ask", json={"question": " Highest product in Q3 "}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["question"] == "Highest product in Q3"
    assert body["agents"] == ["database"]
    assert body["evidence"][0]["product"] == "Q3 winner"
    assert body["answer_mode"] == "evidence"


def test_partial_source_failure(monkeypatch):
    def fail(_):
        raise RuntimeError("sensitive provider details")

    monkeypatch.setattr("app.graph.workflow.run_document_agent", fail)
    monkeypatch.setattr(
        "app.graph.workflow.run_web_agent",
        lambda _: {"agent": "web", "results": [{"title": "Evidence"}]},
    )
    results = agents_node(
        {"question": "candidate online", "selected_agents": ["document", "web"]}
    )["results"]
    assert "sensitive" not in str(results)
    assert results[1]["results"]


def test_index_preserves_other_documents_and_replaces_stale_chunks(monkeypatch):
    with closing(QdrantClient(":memory:")) as client:
        monkeypatch.setattr(vector_store, "get_qdrant_client", lambda: client)
        monkeypatch.setattr(
            vector_store, "embed_documents", lambda chunks: [[1.0, 0.0] for _ in chunks]
        )
        monkeypatch.setattr(vector_store, "embed_query", lambda _: [1.0, 0.0])
        vector_store.index_chunks(["first", "stale"], "a.pdf")
        vector_store.index_chunks(["other"], "b.pdf")
        vector_store.index_chunks(["updated"], "a.pdf")
        results = vector_store.semantic_search("query", limit=10)
        assert {item["text"] for item in results} == {"updated", "other"}
        assert vector_store.document_count() == 2


def test_empty_index_does_not_load_model(monkeypatch):
    with closing(QdrantClient(":memory:")) as client:
        monkeypatch.setattr(vector_store, "get_qdrant_client", lambda: client)
        assert vector_store.semantic_search("query") == []


def test_cross_source_routing():
    assert route_query("Compare candidate skills to current requirements online") == [
        "document",
        "web",
    ]
    assert route_query("revenue in Q4") == ["database"]
