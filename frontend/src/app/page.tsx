"use client";

import { FormEvent, useState } from "react";
import {
  ArrowUp,
  Check,
  Database,
  FileText,
  Globe2,
  Loader2,
  ShieldCheck,
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
          : "Unable to reach backend."
      );
    } finally {
      setLoading(false);
    }
  }

  const agents = result?.agents || [];

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <div className="mark">CR</div>
          <span>COLLAB RAG</span>
        </div>

        <div className="status">
          <span className="dot" />
          SYSTEM ONLINE
        </div>
      </header>

      <section className="hero">
        <div className="eyebrow">
          MULTI-AGENT RETRIEVAL SYSTEM / 01
        </div>

        <h1>
          Intelligence across
          <br />
          every source.
        </h1>

        <p>
          Specialized agents search documents, databases and the web,
          then combine evidence into one response.
        </p>

        <form className="query" onSubmit={submitQuestion}>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask across your knowledge..."
          />

          <button type="submit">
            {loading ? (
              <Loader2 className="spin" size={20} />
            ) : (
              <ArrowUp size={20} />
            )}
          </button>
        </form>

        <div className="examples">
          <button
            onClick={() =>
              setQuestion("What AI skills does the candidate have?")
            }
          >
            Candidate AI skills
          </button>

          <button
            onClick={() =>
              setQuestion("What is the highest selling product in Q3?")
            }
          >
            Highest Q3 sales
          </button>

          <button
            onClick={() =>
              setQuestion(
                "Compare the candidate's AI skills with current AI engineering requirements online."
              )
            }
          >
            Cross-source comparison
          </button>
        </div>
      </section>

      <section className="agents">
        <div className="section-title">
          <span>ACTIVE AGENTS</span>
          <span>03 CONNECTED</span>
        </div>

        <div className="agent-grid">
          <AgentCard
            icon={<FileText size={19} />}
            name="DOCUMENT"
            detail="PDF - Semantic Retrieval"
            active={agents.includes("document")}
          />

          <AgentCard
            icon={<Database size={19} />}
            name="DATABASE"
            detail="SQLite - Structured Data"
            active={agents.includes("database")}
          />

          <AgentCard
            icon={<Globe2 size={19} />}
            name="WEB"
            detail="Live Search"
            active={agents.includes("web")}
          />
        </div>
      </section>

      {(loading || result || error) && (
        <section className="workspace">
          <div className="trace">
            <div className="section-title">
              <span>EXECUTION TRACE</span>
              <span>{loading ? "RUNNING" : "COMPLETE"}</span>
            </div>

            <TraceRow number="01" title="ROUTER" />

            {agents.map((agent, index) => (
              <TraceRow
                key={agent}
                number={`0${index + 2}`}
                title={`${agent.toUpperCase()} AGENT`}
              />
            ))}

            {result && (
              <>
                <TraceRow
                  number={`0${agents.length + 2}`}
                  title="CRITIC"
                />
                <TraceRow
                  number={`0${agents.length + 3}`}
                  title="SYNTHESIS"
                />
              </>
            )}
          </div>

          <div className="response">
            <div className="section-title">
              <span>RESPONSE</span>

              {result && (
                <span className="reviewed">
                  <ShieldCheck size={14} />
                  REVIEWED
                </span>
              )}
            </div>

            {loading && (
              <div className="loading-state">
                Agents are retrieving evidence...
              </div>
            )}

            {error && <div className="error">{error}</div>}

            {result && (
              <>
                <span className="mini-label">QUERY</span>
                <h2>{result.question}</h2>

                <span className="mini-label">EVIDENCE</span>
                <pre>{result.answer}</pre>
              </>
            )}
          </div>
        </section>
      )}

      <footer>
        <span>MULTI-AGENT COLLABORATIVE RAG</span>
        <span>LANGGRAPH / FASTAPI / QDRANT</span>
      </footer>
    </main>
  );
}

function AgentCard({
  icon,
  name,
  detail,
  active,
}: {
  icon: React.ReactNode;
  name: string;
  detail: string;
  active: boolean;
}) {
  return (
    <div className={`agent-card ${active ? "active" : ""}`}>
      <div className="icon">{icon}</div>

      <div>
        <strong>{name}</strong>
        <span>{detail}</span>
      </div>

      <div className="agent-status">
        {active && <Check size={12} />}
        {active ? "USED" : "READY"}
      </div>
    </div>
  );
}

function TraceRow({
  number,
  title,
}: {
  number: string;
  title: string;
}) {
  return (
    <div className="trace-row">
      <span>{number}</span>
      <strong>{title}</strong>
      <Check size={15} />
    </div>
  );
}
