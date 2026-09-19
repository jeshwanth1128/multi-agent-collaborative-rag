import "server-only";

const headers = { "Cache-Control": "no-store" };

export async function backendRequest(path: "/ask" | "/sources", question?: string) {
  const configuredUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL;
  if (!configuredUrl && process.env.NODE_ENV === "production") {
    return Response.json({ detail: "The workspace API is not configured. Please contact the administrator." }, { status: 503, headers });
  }
  let base: URL;
  try {
    base = new URL(configuredUrl || "http://127.0.0.1:8000");
    if (!['http:', 'https:'].includes(base.protocol) || base.username || base.password || base.search || base.hash) throw new Error("Invalid API URL");
    if (process.env.VERCEL === "1" && (base.protocol !== 'https:' || ['localhost', '127.0.0.1', '[::1]'].includes(base.hostname))) throw new Error("Production requires an HTTPS API");
  } catch {
    return Response.json({ detail: "The workspace API configuration is invalid." }, { status: 503, headers });
  }
  try {
    const response = await fetch(`${base.toString().replace(/\/$/, '')}${path}`, {
      method: question === undefined ? "GET" : "POST",
      headers: {
        "Content-Type": "application/json",
        ...(process.env.BACKEND_API_KEY ? { "X-API-Key": process.env.BACKEND_API_KEY } : {}),
      },
      body: question === undefined ? undefined : JSON.stringify({ question }),
      cache: "no-store",
      signal: AbortSignal.timeout(path === "/ask" ? 50000 : 15000),
      redirect: "error",
    });
    if (!response.ok) {
      const status = response.status === 429 ? 429 : 503;
      return Response.json({ detail: status === 429 ? "The workspace is busy. Please try again shortly." : "The retrieval service is unavailable. Please retry or contact the administrator." }, { status, headers: { ...headers, ...(status === 429 ? { "Retry-After": "10" } : {}) } });
    }
    const data = await response.json();
    if (path === "/ask" && (typeof data.answer !== "string" || !Array.isArray(data.evidence) || !Array.isArray(data.agents))) throw new Error("Invalid API response");
    if (path === "/sources" && !data.sources) throw new Error("Invalid API response");
    return Response.json(data, { headers });
  } catch (error) {
    const timeout = error instanceof Error && error.name === "TimeoutError";
    return Response.json({ detail: timeout ? "Retrieval took too long. The service may be warming up; please retry shortly." : "Unable to reach the retrieval service. Please try again." }, { status: timeout ? 504 : 502, headers });
  }
}
