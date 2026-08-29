from pathlib import Path
from app.pipeline import pipeline

folder = Path("data/sample_patient_01")
initial_state = {
    "doctor_notes_raw": (folder / "doctor_notes.txt").read_text(),
    "lab_report_raw": (folder / "lab_report.txt").read_text(),
    "prescription_raw": (folder / "prescription.txt").read_text(),
}

result = pipeline.invoke(initial_state)

print("KEYS PRESENT:", list(result.keys()))
print()
for key, value in result.items():
    print(f"--- {key} ---")
    print(value)
    print()