import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const authorization = request.headers.get("authorization");
  if (!authorization?.startsWith("Bearer ")) {
    return NextResponse.json({ error: "Missing bearer token" }, { status: 401 });
  }

  // TODO: Validate the Auth0 JWT against AUTH0_DOMAIN/AUTH0_AUDIENCE.
  // Never trust the Android client to identify the user.
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) return NextResponse.json({ error: "Server is not configured" }, { status: 500 });

  const response = await fetch("https://api.openai.com/v1/realtime/client_secrets", {
    method: "POST",
    headers: { "Authorization": "Bearer " + apiKey, "Content-Type": "application/json" },
    body: JSON.stringify({ session: { type: "realtime", model: "gpt-realtime-2.1" } }),
  });

  return new NextResponse(await response.text(), {
    status: response.status,
    headers: { "Content-Type": "application/json" },
  });
}
