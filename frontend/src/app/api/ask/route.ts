import { backendRequest } from "@/lib/backend";

export const runtime = "nodejs";
export const maxDuration = 60;

export async function POST(request: Request) {
  // Bound streamed bodies too, not only clients that supply Content-Length.
  const reader = request.body?.getReader();
  if (!reader) return Response.json({ detail: "A question is required." }, { status: 400 });
  let bytes = 0;
  let text = "";
  const decoder = new TextDecoder();
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      bytes += value.byteLength;
      if (bytes > 16000) {
        await reader.cancel();
        return Response.json({ detail: "The question is too long." }, { status: 413 });
      }
      text += decoder.decode(value, { stream: true });
    }
    text += decoder.decode();
    const body = JSON.parse(text);
    if (typeof body?.question !== "string" || !body.question.trim() || body.question.trim().length > 2000) {
      return Response.json({ detail: "Enter a question between 1 and 2,000 characters." }, { status: 422 });
    }
    return backendRequest("/ask", body.question.trim());
  } catch {
    return Response.json({ detail: "The request must contain valid JSON." }, { status: 400 });
  } finally {
    reader.releaseLock();
  }
}
