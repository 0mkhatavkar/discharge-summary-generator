import requests
from pathlib import Path

folder = Path("data/sample_patient_01")
files = {
    "doctor_notes_image": open(folder / "doctor_notes_scan.png", "rb"),
    "lab_report_image": open(folder / "lab_report_scan.png", "rb"),
    "prescription_image": open(folder / "prescription_scan.png", "rb"),
}

response = requests.post(
    "https://discharge-summary-generator-fb72.onrender.com/discharge-summary-from-images",
    files=files,
)
print(response.status_code)
print(response.json())