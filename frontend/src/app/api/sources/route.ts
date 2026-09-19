import { backendRequest } from "@/lib/backend";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 20;

export async function GET() {
  return backendRequest("/sources");
}
