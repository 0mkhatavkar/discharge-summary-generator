"""
Reconciliation Agent
---------------------
Cross-checks extracted medications against extracted lab values using a small
rule-based knowledge base of well-established renal-dosing / lab-interaction
concerns. Deterministic on purpose -- for a safety-relevant check, a fixed
rule set is more trustworthy and testable than another LLM call that could
hallucinate a threshold.

NOTE: this rule set is illustrative for a portfolio demo, not a substitute
for a validated clinical drug-interaction database (e.g. Lexicomp/Micromedex).
"""
import json

DOSING_RULES = [
    {"drug": "vancomycin", "lab_test": "egfr", "comparison": "below", "threshold": 50, "severity": "moderate",
     "concern": "Standard interval dosing without adjustment risks toxic accumulation when renal clearance is reduced."},
    {"drug": "metformin", "lab_test": "egfr", "comparison": "below", "threshold": 30, "severity": "high",
     "concern": "Contraindicated below eGFR 30 due to risk of lactic acidosis."},
    {"drug": "lisinopril", "lab_test": "potassium", "comparison": "above", "threshold": 5.0, "severity": "moderate",
     "concern": "ACE inhibitors can worsen hyperkalemia; potassium is already elevated."},
]


def _find_lab_value(lab_values, test_name):
    """Match by substring (case-insensitive). If a test appears twice (e.g. baseline
    vs current creatinine, like we saw earlier), prefer the non-baseline (current) one."""
    matches = [lab for lab in lab_values if test_name.lower() in lab.get("test", "").lower()]
    if not matches:
        return None
    non_baseline = [m for m in matches if "baseline" not in m.get("test", "").lower()]
    return (non_baseline or matches)[0]


def run_reconciliation(state: dict) -> dict:
    extracted = state.get("extracted_data") or {}
    medications = extracted.get("medications", [])
    lab_values = extracted.get("lab_values", [])

    conflicts = []
    med_names = {m.get("name", "").lower() for m in medications if m.get("name")}

    for rule in DOSING_RULES:
        if rule["drug"] not in med_names:
            continue
        lab = _find_lab_value(lab_values, rule["lab_test"])
        if lab is None or not isinstance(lab.get("value"), (int, float)):
            continue
        value = lab["value"]
        triggered = (value < rule["threshold"]) if rule["comparison"] == "below" else (value > rule["threshold"])
        if triggered:
            conflicts.append({
                "medication": rule["drug"],
                "lab_test": lab["test"],
                "lab_value": value,
                "threshold": rule["threshold"],
                "concern": rule["concern"],
                "severity": rule["severity"],
            })

    state["conflicts"] = conflicts
    return state


if __name__ == "__main__":
    # A fixed test fixture matching extraction's output shape -- no LLM call needed,
    # so this runs instantly and free, every time.
    test_state = {"extracted_data": {
        "medications": [
            {"name": "Vancomycin", "dose": "1g", "frequency": "q8h", "route": "IV"},
            {"name": "Lisinopril", "dose": "10mg", "frequency": "once daily", "route": "PO"},
            {"name": "Metformin", "dose": "1000mg", "frequency": "twice daily", "route": "PO"},
            {"name": "Acetaminophen", "dose": "500mg", "frequency": "q6h PRN pain", "route": "PO"},
        ],
        "lab_values": [
            {"test": "Baseline creatinine", "value": 1.6, "unit": "mg/dL", "flag": None},
            {"test": "Potassium", "value": 5.2, "unit": "mmol/L", "flag": "HIGH"},
            {"test": "Creatinine", "value": 2.1, "unit": "mg/dL", "flag": "HIGH"},
            {"test": "eGFR", "value": 27, "unit": "mL/min/1.73m2", "flag": "LOW"},
        ],
    }}
    result = run_reconciliation(test_state)
    print(json.dumps(result["conflicts"], indent=2))