import json
from app.llm_client import call_llm

EXTRACTION_SYSTEM_PROMPT = (
    "You are a clinical data extraction assistant. Extract structured "
    "information from hospital discharge documents. Always respond with "
    "valid JSON only -- no markdown, no explanation, no code fences."
)

EXTRACTION_TEMPLATE = """Extract these fields from the clinical document below, as JSON.
If a field isn't mentioned, use null (or an empty list for list fields). Do not invent values.
Extract the actual clinical content, not field labels -- for example, if the text says
"Admitting Diagnosis: pneumonia", extract "pneumonia", not "Admitting Diagnosis".
For each lab value, set "timing" to "baseline" if the text explicitly calls it a baseline or prior value, "current" if it's from a lab report or a recent result, or null if unclear.

Return exactly this structure:
{{
  "patient_info": {{"name": null, "mrn": null, "dob": null, "admission_date": null, "discharge_date": null}},
  "diagnoses": [],
  "medications": [{{"name": null, "dose": null, "frequency": null, "route": null}}],
  "lab_values": [{{"test": null, "value": null, "unit": null, "flag": null, "timing": null}}],
  "follow_up": []
}}

Document:
\"\"\"
{raw_text}
\"\"\"
"""


def _parse_json_response(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned.lstrip("`")
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    return json.loads(cleaned.strip())


def _flatten_list_field(items, dict_keys):
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
    for lab in lab_values or []:
        try:
            lab["value"] = float(lab["value"])
        except (TypeError, ValueError):
            pass
    return lab_values


def _has_junk(parsed: dict) -> bool:
    for field in ("diagnoses", "follow_up"):
        if any(item == "" for item in (parsed.get(field) or [])):
            return True
    for med in parsed.get("medications") or []:
        if isinstance(med, dict) and not any(med.values()):
            return True
    return False


def _clean_extraction(parsed: dict) -> dict:
    parsed["diagnoses"] = [d for d in (parsed.get("diagnoses") or []) if d]
    parsed["follow_up"] = [f for f in (parsed.get("follow_up") or []) if f]
    parsed["medications"] = [m for m in (parsed.get("medications") or []) if isinstance(m, dict) and any(m.values())]
    return parsed


def _looks_incomplete(raw_text: str, parsed: dict) -> bool:
    FIELD_KEYWORDS = {
        "diagnoses": ["diagnosis"],
        "follow_up": ["follow-up", "follow up"],
    }
    text_lower = raw_text.lower()
    for field, keywords in FIELD_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords) and not parsed.get(field):
            return True
    return False


def _extract_one(raw_text: str) -> dict:
    prompt = EXTRACTION_TEMPLATE.format(raw_text=raw_text)
    parsed = {}
    for attempt in range(2):
        response_text = call_llm(prompt, system=EXTRACTION_SYSTEM_PROMPT, temperature=0.1)
        parsed = _parse_json_response(response_text)
        parsed["diagnoses"] = _flatten_list_field(parsed.get("diagnoses"), ["name", "type"])
        parsed["follow_up"] = _flatten_list_field(parsed.get("follow_up"), ["provider", "timing"])
        parsed["lab_values"] = _coerce_lab_values(parsed.get("lab_values"))
        if not _has_junk(parsed) and not _looks_incomplete(raw_text, parsed):
            break
    return _clean_extraction(parsed)


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
    parts = [_extract_one(raw_text) for raw_text in documents if raw_text.strip()]
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