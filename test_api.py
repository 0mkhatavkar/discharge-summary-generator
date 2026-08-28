import requests
from pathlib import Path

folder = Path("data/sample_patient_01")
payload = {
    "doctor_notes_raw": (folder / "doctor_notes.txt").read_text(),
    "lab_report_raw": (folder / "lab_report.txt").read_text(),
    "prescription_raw": (folder / "prescription.txt").read_text(),
}

response = requests.post("http://127.0.0.1:8000/discharge-summary", json=payload)
print(response.status_code)
print(response.json())