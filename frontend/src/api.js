const API_BASE_URL = "http://localhost:8000";

export async function generateDischargeSummary(payload) {
  const response = await fetch(`${API_BASE_URL}/discharge-summary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}