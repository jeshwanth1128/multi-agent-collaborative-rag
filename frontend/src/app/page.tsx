"use client";

import Link from "next/link";
import { FormEvent, ReactNode, useCallback, useEffect, useRef, useState } from "react";
import { ArrowUp, CheckCircle2, Database, FileText, Globe2, Loader2, RotateCcw, X } from "lucide-react";

type Evidence = {
  id: number; agent: string; text?: string; source?: string;
  title?: string; snippet?: string; url?: string;
  product?: string; quarter?: string; revenue?: number;
};
type ApiResponse = {
  question: string; agents: string[]; answer: string; answer_mode: string;
  critique: { passed?: boolean; failed_agents?: string[] };
  evidence: Evidence[]; warnings: string[];
};
type SourceStatus = { status: string; detail: string };
type Sources = Record<string, SourceStatus>;

const examples = [
  { label: "Candidate skills", question: "What AI skills does the candidate have?" },
  { label: "Q3 sales", question: "What is the highest selling product in Q3?" },
  { label: "Cross-source query", question: "Compare the candidate's AI skills with current AI engineering requirements online." },
];

export default function Home() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sources, setSources] = useState<Sources | null>(null);
  const [sourceError, setSourceError] = useState("");
  const [checking, setChecking] = useState(true);
  const [lastQuestion, setLastQuestion] = useState("");
  const request = useRef<AbortController | null>(null);
  const textarea = useRef<HTMLTextAreaElement>(null);

  const refreshSources = useCallback(async (signal?: AbortSignal) => {
    try {
      const response = await fetch("/api/sources", { signal: signal ? AbortSignal.any([signal, AbortSignal.timeout(20000)]) : AbortSignal.timeout(20000) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Source status is unavailable.");
      setSources(data.sources);
    } catch (err) {
      if (signal?.aborted) return;
      setSources(null);
      setSourceError(err instanceof Error ? err.message : "Source status is unavailable.");
    } finally {
      if (!signal?.aborted) setChecking(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/sources", { signal: AbortSignal.any([controller.signal, AbortSignal.timeout(20000)]) })
      .then(async response => {
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Source status is unavailable.");
        return data.sources as Sources;
      })
      .then(data => { if (!controller.signal.aborted) setSources(data); })
      .catch(err => { if (!controller.signal.aborted) setSourceError(err instanceof Error ? err.message : "Source status is unavailable."); })
      .finally(() => { if (!controller.signal.aborted) setChecking(false); });
    return () => { controller.abort(); request.current?.abort(); };
  }, []);

  async function ask(value: string) {
    const submitted = value.trim();
    if (!submitted || submitted.length > 2000 || request.current) return;
    const controller = new AbortController();
    request.current = controller;
    setLoading(true);
    setError("");
    setResult(null);
    setLastQuestion(submitted);
    try {
      const response = await fetch("/api/ask", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: submitted }),
        signal: AbortSignal.any([controller.signal, AbortSignal.timeout(55000)]),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "The query could not be completed.");
      setResult(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "";
      setError(controller.signal.aborted
        ? "Request cancelled. You can edit your question and try again."
        : err instanceof Error && err.name === "TimeoutError"
          ? "The request timed out. Please try again shortly."
          : message === "Failed to fetch"
            ? "The app lost its connection to the local server. Make sure both the frontend and API are running, then try again."
            : message || "Unable to retrieve an answer.");
    } finally {
      request.current = null;
      setLoading(false);
    }
  }

  function submitQuestion(event: FormEvent) {
    event.preventDefault();
    void ask(question);
  }

  const agents = result?.agents || [];
  const used = result?.evidence.map(item => item.agent) || [];
  const readyCount = Object.values(sources || {}).filter(source => source.status === "ready").length;

  return (
    <main className="app-shell">
      <a className="skip-link" href="#question">Skip to question</a>
      <header className="header">
        <Link className="brand" href="/" aria-label="RAG Workspace home">
          <div className="product-name"><span className="brand-mark" aria-hidden="true" />RAG WORKSPACE</div>
          <div className="product-subtitle">One question. A clearer picture.</div>
        </Link>
        <div className="stack-label">DOCUMENTS / DATA / WEB</div>
      </header>

      <section className="query-section" aria-labelledby="query-heading">
        <div className="query-copy">
          <span className="kicker">MULTI-SOURCE RESEARCH</span>
          <h1 id="query-heading">Your knowledge.<br />Working together.</h1>
          <p>Ask across your documents, sales data, and the web. Follow the evidence from each source to one grounded response.</p>
        </div>
        <form onSubmit={submitQuestion}>
          <label htmlFor="question" className="query-label">What would you like to find out?</label>
          <div className="query-box">
            <textarea id="question" ref={textarea} value={question} maxLength={2000} rows={3}
              onChange={event => setQuestion(event.target.value)}
              onKeyDown={event => { if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) { event.preventDefault(); void ask(question); } }}
              placeholder="Ask a question across your connected knowledge…"
              aria-describedby="query-hint" required />
            <button type="submit" disabled={!question.trim() || loading} aria-label="Ask question" title="Ask question">
              {loading ? <Loader2 size={20} className="spin" aria-hidden="true" /> : <ArrowUp size={20} aria-hidden="true" />}
            </button>
          </div>
          <div id="query-hint" className="query-hint"><span>Ctrl / ⌘ + Enter to ask</span><span>{question.length.toLocaleString()} / 2,000</span></div>
        </form>
        <div className="quick-queries" aria-label="Example questions">
          <span>TRY A QUESTION</span>
          {examples.map(example => <button key={example.label} disabled={loading} onClick={() => { setQuestion(example.question); textarea.current?.focus(); }}>{example.label}</button>)}
        </div>
      </section>

      <section className="sources-section" aria-labelledby="sources-heading">
        <div className="section-header">
          <h2 id="sources-heading">SOURCES</h2>
          <button className="text-button" onClick={() => { setChecking(true); setSourceError(""); void refreshSources(); }} disabled={checking} aria-label="Refresh source status">
            <RotateCcw size={12} aria-hidden="true" />{checking ? "CHECKING" : sources ? `${readyCount} LOCAL SOURCES READY` : "RETRY STATUS"}
          </button>
        </div>
        {sourceError && <p className="source-notice" role="status">{sourceError}</p>}
        <div className="source-grid">
          <SourceCard icon={<FileText size={20} />} title="Documents" description="PDF passages & semantic search" status={sources?.document} active={used.includes("document")} checking={checking} />
          <SourceCard icon={<Database size={20} />} title="Database" description="Sales by product & quarter" status={sources?.database} active={used.includes("database")} checking={checking} />
          <SourceCard icon={<Globe2 size={20} />} title="Web" description="Current public search results" status={sources?.web} active={used.includes("web")} checking={checking} />
        </div>
      </section>

      <div aria-live="polite" aria-atomic="false">
        {(loading || result || error) && <section className="result-layout" aria-label="Query results" aria-busy={loading}>
          <aside className="steps-panel">
            <div className="section-header"><h2>RETRIEVAL</h2><span>{loading ? "IN PROGRESS" : error ? "NOT COMPLETED" : result?.evidence.length ? "COMPLETE" : "NO MATCHES"}</span></div>
            <p className="retrieval-caption">{loading ? "Finding relevant sources and gathering evidence for your question." : error ? "Your question is saved. Retry when you’re ready." : "Sources selected for this question."}</p>
            {agents.map((agent, index) => <div className="step-row" key={agent}>
              <span className="step-number">{String(index + 1).padStart(2, "0")}</span>
              <div><div className="step-title">{agent === "document" ? "Documents" : agent === "database" ? "Database" : "Web"}</div><div className="step-description">{used.includes(agent) ? `${result?.evidence.filter(item => item.agent === agent).length} evidence items retrieved` : "No evidence returned"}</div></div>
            </div>)}
          </aside>
          <section className="response-panel" aria-labelledby="response-heading">
            <div className="section-header"><h2 id="response-heading">{result?.answer_mode === "evidence" ? "RETRIEVED EVIDENCE" : "RESPONSE"}</h2>
              {result?.evidence.length ? <span className="review-status"><CheckCircle2 size={14} aria-hidden="true" />{result.evidence.length} sources of evidence</span> : null}
            </div>
            {loading && <div className="loading-state"><Loader2 size={20} className="spin" aria-hidden="true" /><p>Gathering the evidence<span>This can take a moment on the first query.</span></p><button className="text-button" onClick={() => request.current?.abort()}><X size={14} aria-hidden="true" />Cancel</button></div>}
            {error && <div className="error-message" role="alert"><p>{error}</p><button className="text-button" onClick={() => void ask(lastQuestion)}><RotateCcw size={14} aria-hidden="true" />Try again</button></div>}
            {result && <>
              <h3 className="response-query">{result.question}</h3>
              {result.warnings.length > 0 && <div className="warning-message">{result.warnings.map(warning => <p key={warning}>{warning}</p>)}</div>}
              <div className="response-answer">{result.answer}</div>
              {result.evidence.length > 0 && <div className="evidence-list"><h3>Explore the evidence</h3>{result.evidence.map(item => <EvidenceRow key={item.id} item={item} />)}</div>}
              <p className="answer-note">{result.answer_mode === "generated" ? "Generated from retrieved evidence. Review the sources before relying on the answer." : "Direct source excerpts. No generated interpretation was added."}</p>
            </>}
          </section>
        </section>}
      </div>
      <footer className="footer"><span>Multi-Agent Collaborative RAG</span><span>Traceable by design.</span></footer>
    </main>
  );
}

function SourceCard({ icon, title, description, status, active, checking }: { icon: ReactNode; title: string; description: string; status?: SourceStatus; active: boolean; checking: boolean }) {
  return <div className={`source-card ${active ? "source-active" : ""}`}>
    <div className="source-icon" aria-hidden="true">{icon}</div>
    <div><h3 className="source-title">{title}</h3><div className="source-description">{description}</div><div className="source-detail">{status?.detail || (checking ? "Checking source…" : "Status unavailable")}</div></div>
    <span className="source-state">{active ? "USED" : checking ? "CHECKING" : (status?.status || "UNKNOWN").toUpperCase()}</span>
  </div>;
}

function EvidenceRow({ item }: { item: Evidence }) {
  const title = item.agent === "document" ? item.source : item.agent === "database" ? `${item.product} / ${item.quarter}` : item.title;
  const safeUrl = item.url && /^https?:\/\//i.test(item.url) ? item.url : null;
  return <details className="evidence-item"><summary><span className="citation">[{item.id}]</span><span>{title || item.agent}</span><span className="evidence-type">{item.agent}</span></summary>
    <div className="evidence-body">{item.text || item.snippet || (typeof item.revenue === "number" ? `Revenue: ${item.revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : "No preview available.")}
      {safeUrl && <a href={safeUrl} target="_blank" rel="noopener noreferrer">Open source ↗</a>}
    </div>
  </details>;
}
