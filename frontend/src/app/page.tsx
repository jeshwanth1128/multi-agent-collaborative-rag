"use client";

import { FormEvent, useState } from "react";
import {
  ArrowUp,
  CheckCircle2,
  Database,
  FileText,
  Globe2,
  Loader2,
} from "lucide-react";

type ApiResponse = {
  question: string;
  agents: string[];
  critique: {
    passed?: boolean;
  };
  answer: string;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submitQuestion(event: FormEvent) {
    event.preventDefault();

    if (!question.trim() || loading) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to reach the backend."
      );
    } finally {
      setLoading(false);
    }
  }

  const agents = result?.agents || [];

  return (
    <main className="app-shell">
      <header className="header">
        <div>
          <div className="product-name">RAG WORKSPACE</div>
          <div className="product-subtitle">
            Multi-source retrieval orchestration
          </div>
        </div>

        <div className="stack-label">
          LangGraph / FastAPI / Qdrant
        </div>
      </header>

      <section className="query-section">
        <div className="query-copy">
          <span className="kicker">QUERY</span>

          <h1>
            Search documents, structured data,
            and the web in one workflow.
          </h1>

          <p>
            The system routes each question to the right retrieval
            source, gathers evidence, checks it, and returns a grounded
            response.
          </p>
        </div>

        <form className="query-box" onSubmit={submitQuestion}>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question across your connected knowledge..."
          />

          <button type="submit" disabled={loading}>
            {loading ? (
              <Loader2 size={18} className="spin" />
            ) : (
              <ArrowUp size={18} />
            )}
          </button>
        </form>

        <div className="quick-queries">
          <button
            onClick={() =>
              setQuestion("What AI skills does the candidate have?")
            }
          >
            Candidate skills
          </button>

          <button
            onClick={() =>
              setQuestion("What is the highest selling product in Q3?")
            }
          >
            Q3 sales
          </button>

          <button
            onClick={() =>
              setQuestion(
                "Compare the candidate's AI skills with current AI engineering requirements online."
              )
            }
          >
            Cross-source query
          </button>
        </div>
      </section>

      <section className="sources-section">
        <div className="section-header">
          <span>SOURCES</span>
          <span>3 CONNECTED</span>
        </div>

        <div className="source-grid">
          <SourceCard
            icon={<FileText size={18} />}
            title="Documents"
            description="PDF retrieval and semantic search"
            active={agents.includes("document")}
          />

          <SourceCard
            icon={<Database size={18} />}
            title="Database"
            description="Structured SQLite records"
            active={agents.includes("database")}
          />

          <SourceCard
            icon={<Globe2 size={18} />}
            title="Web"
            description="External search results"
            active={agents.includes("web")}
          />
        </div>
      </section>

      {(loading || result || error) && (
        <section className="result-layout">
          <aside className="steps-panel">
            <div className="section-header">
              <span>RETRIEVAL STEPS</span>
              <span>{loading ? "RUNNING" : "COMPLETE"}</span>
            </div>

            <Step
              number="01"
              title="Route query"
              description="Identify required data sources"
            />

            {agents.map((agent, index) => (
              <Step
                key={agent}
                number={`0${index + 2}`}
                title={`Search ${agent}`}
                description="Retrieve relevant evidence"
              />
            ))}

            {result && (
              <>
                <Step
                  number={`0${agents.length + 2}`}
                  title="Check evidence"
                  description="Validate retrieval quality"
                />

                <Step
                  number={`0${agents.length + 3}`}
                  title="Compose response"
                  description="Merge retrieved evidence"
                />
              </>
            )}
          </aside>

          <section className="response-panel">
            <div className="section-header">
              <span>RESPONSE</span>
              {result?.critique?.passed && (
                <span className="review-status">
                  <CheckCircle2 size={14} />
                  Evidence checked
                </span>
              )}
            </div>

            {loading && (
              <div className="loading-state">
                Retrieving evidence...
              </div>
            )}

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            {result && (
              <>
                <div className="response-query">
                  {result.question}
                </div>

                <pre className="response-answer">
                  {result.answer}
                </pre>
              </>
            )}
          </section>
        </section>
      )}

      <footer className="footer">
        <span>Multi-Agent Collaborative RAG</span>
        <span>Document / Database / Web</span>
      </footer>
    </main>
  );
}

function SourceCard({
  icon,
  title,
  description,
  active,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  active: boolean;
}) {
  return (
    <div className={`source-card ${active ? "source-active" : ""}`}>
      <div className="source-icon">{icon}</div>

      <div>
        <div className="source-title">{title}</div>
        <div className="source-description">{description}</div>
      </div>

      <div className="source-state">
        {active ? "USED" : "READY"}
      </div>
    </div>
  );
}

function Step({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="step-row">
      <div className="step-number">{number}</div>

      <div>
        <div className="step-title">{title}</div>
        <div className="step-description">{description}</div>
      </div>
    </div>
  );
}
