# RAG Workspace

Next.js 16 / React 19 frontend and Python 3.12 FastAPI / LangGraph backend. Questions are routed to local document search (MiniLM embeddings + Qdrant), a read-only SQLite sales database, and public web search. Gemini optionally composes an answer with numbered evidence references; unavailable generation returns clearly labelled excerpts instead.

## Local setup

From the repository root:

```sh
uv sync --frozen
# Copy .env.example to .env; preserve existing credentials if already configured.
uv run python -m scripts.create_sample_db
uv run python -m scripts.ingest_documents path/to/document.pdf
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Index documents before starting the API when using embedded Qdrant: only one process can own its storage. Re-indexing replaces that source while preserving other documents. The demo database command never overwrites an existing database. Document parsing and the first embedding query download model files; allow network access and sufficient memory.

In another terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open http://localhost:3000. Local development defaults to port 8000. The browser calls same-origin `/api/ask` and `/api/sources`; only the Next.js server connects to the Python API. No browser CORS configuration is required. For a local production preview, set `API_URL=http://127.0.0.1:8000` explicitly, then run `npm run build` and `npm start`.

## Production: Vercel frontend + Render backend

1. Set the Vercel project **Root Directory** to `frontend`, framework Next.js, install command `npm ci`, build command `npm run build`. The Python ML stack runs on Render, not in a Vercel function.
2. `render.yaml` configures one Python worker, a health check and a persistent disk. Its Standard plan and disk incur Render charges when deployed; no deployment is performed by editing this file.
3. Set Vercel **API_URL** to the HTTPS origin of the deployed Render service. Set **BACKEND_API_KEY** to the same secret generated for Render. Never prefix secrets with NEXT_PUBLIC_. Redeploy after changing environment variables. The old NEXT_PUBLIC_API_URL remains accepted for compatibility, but API_URL is preferred.
4. Set **GEMINI_API_KEY** on Render for generated answers. It is optional for retrieval-only use. Model failures are reported and evidence remains available.
5. Provision sales data at DATABASE_PATH and index approved documents into QDRANT_PATH on the persistent disk. Your laptop's SQLite and Qdrant files are not deployed by Git. For demo sales, run `uv run python -m scripts.create_sample_db` in the Render shell. Ingest documents while the embedded index is not held by a running process, or use hosted Qdrant via QDRANT_URL and QDRANT_API_KEY for concurrent ingestion and multiple workers. Do not publish private sample documents without reviewing them.
6. `/health` is liveness; `/sources` reports actual source readiness (requires the backend key). Web search is marked available, not falsely verified connected. Check it with a real query after deployment.

**Access model:** the website currently has no end-user accounts. The server key protects direct access to the Python API, not access through the website. Use Vercel Deployment Protection or your organization's authenticated gateway before exposing private documents. Public deployment is suitable only for public/demo data. The API limits concurrent expensive queries; use platform rate limiting for public traffic.

## Verification

```sh
uv run pytest tests -q
uv run ruff check app tests scripts
cd frontend
npm run lint
npx tsc --noEmit
npm run build
```

Regression tests cover validation, production authorization, quarter filtering, totals, missing storage, multi-source failure isolation, non-destructive document indexing, and the real database workflow. External web and Gemini availability depends on network and provider quotas. The database agent supports the existing sales schema, quarter/product filtering, top/lowest records and revenue totals; it is not arbitrary natural-language SQL. Evidence checks confirm retrieval presence, not factual correctness.
