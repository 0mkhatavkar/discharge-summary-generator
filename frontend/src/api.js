const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

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
export async function generateDischargeSummaryFromImages(images) {
  const formData = new FormData();
  formData.append("doctor_notes_image", images.doctorNotes);
  formData.append("lab_report_image", images.labReport);
  formData.append("prescription_image", images.prescription);

  const response = await fetch(`${API_BASE_URL}/discharge-summary-from-images`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}