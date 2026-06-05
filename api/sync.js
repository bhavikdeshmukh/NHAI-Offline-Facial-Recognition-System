export default function handler(request, response) {
  if (request.method !== "POST") {
    response.status(405).json({ ok: false, error: "Method not allowed" });
    return;
  }

  const events = Array.isArray(request.body?.events) ? request.body.events : [];

  response.status(200).json({
    ok: true,
    received: events.length,
    syncedAt: new Date().toISOString(),
    target: "Datalake 3.0 sync simulation",
  });
}
