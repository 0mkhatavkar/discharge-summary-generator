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


def _flatten_list_field(items, dict_keys):
    """The model sometimes returns list items as plain strings, sometimes as small
    dicts -- normalize both into plain strings so downstream code has one shape to rely on."""
    flat = []
    for item in items or []:
        if isinstance(item, str):
            flat.append(item)
        elif isinstance(item, dict):
            flat.append(" - ".join(str(item[k]) for k in dict_keys if item.get(k)))
        else:
            flat.append(str(item))
    return flat


def _coerce_lab_values(lab_values):
    """Lab 'value' sometimes comes back as a string, sometimes a number --
    normalize to float so reconciliation can compare thresholds reliably."""
    for lab in lab_values or []:
        try:
            lab["value"] = float(lab["value"])
        except (TypeError, ValueError):
            pass  # keep as-is if it's not a clean number (e.g. "trace", "positive")
    return lab_values


def _merge_extractions(parts: list) -> dict:
    merged = {"patient_info": {}, "diagnoses": [], "medications": [], "lab_values": [], "follow_up": []}
    for part in parts:
        for key, value in (part.get("patient_info") or {}).items():
            if value and not merged["patient_info"].get(key):
                merged["patient_info"][key] = value
        merged["diagnoses"] += part.get("diagnoses") or []
        merged["medications"] += part.get("medications") or []
        merged["lab_values"] += part.get("lab_values") or []
        merged["follow_up"] += part.get("follow_up") or []
    return merged


def run_extraction(state: dict) -> dict:
    documents = [
        state.get("doctor_notes_raw", ""),
        state.get("lab_report_raw", ""),
        state.get("prescription_raw", ""),
    ]
    parts = []
    for raw_text in documents:
        if not raw_text.strip():
            continue
        prompt = EXTRACTION_TEMPLATE.format(raw_text=raw_text)
        response_text = call_llm(prompt, system=EXTRACTION_SYSTEM_PROMPT)
        parsed = _parse_json_response(response_text)
        parsed["diagnoses"] = _flatten_list_field(parsed.get("diagnoses"), ["name", "type"])
        parsed["follow_up"] = _flatten_list_field(parsed.get("follow_up"), ["provider", "timing"])
        parsed["lab_values"] = _coerce_lab_values(parsed.get("lab_values"))
        parts.append(parsed)
    state["extracted_data"] = _merge_extractions(parts)
    return state


if __name__ == "__main__":
    from pathlib import Path

    folder = Path("data/sample_patient_01")
    test_state = {
        "doctor_notes_raw": (folder / "doctor_notes.txt").read_text(),
        "lab_report_raw": (folder / "lab_report.txt").read_text(),
        "prescription_raw": (folder / "prescription.txt").read_text(),
    }
    result = run_extraction(test_state)
    print(json.dumps(result["extracted_data"], indent=2))