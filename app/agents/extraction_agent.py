import json
from app.llm_client import call_llm

EXTRACTION_SYSTEM_PROMPT = (
    "You are a clinical data extraction assistant. Extract structured "
    "information from hospital discharge documents. Always respond with "
    "valid JSON only -- no markdown, no explanation, no code fences."
)

EXTRACTION_TEMPLATE = """Extract these fields from the clinical document below, as JSON.
If a field isn't mentioned, use null (or an empty list for list fields). Do not invent values.

Return exactly this structure:
{{
  "patient_info": {{"name": null, "mrn": null, "dob": null, "admission_date": null, "discharge_date": null}},
  "diagnoses": [],
  "medications": [{{"name": null, "dose": null, "frequency": null, "route": null}}],
  "lab_values": [{{"test": null, "value": null, "unit": null, "flag": null}}],
  "follow_up": []
}}

Document:
\"\"\"
{raw_text}
\"\"\"
"""

def _parse_json_response(text: str) -> dict:
    """LLMs sometimes wrap JSON in ```json fences despite instructions -- strip those."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned.lstrip("`")
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    return json.loads(cleaned.strip())


def run_extraction(state: dict) -> dict:
    raw_text = state.get("doctor_notes_raw", "")
    prompt = EXTRACTION_TEMPLATE.format(raw_text=raw_text)
    response_text = call_llm(prompt, system=EXTRACTION_SYSTEM_PROMPT)
    state["extracted_data"] = _parse_json_response(response_text)
    return state

if __name__ == "__main__":
    from pathlib import Path

    notes_text = Path("data/sample_patient_01/doctor_notes.txt").read_text()
    result = run_extraction({"doctor_notes_raw": notes_text})
    print(json.dumps(result["extracted_data"], indent=2))