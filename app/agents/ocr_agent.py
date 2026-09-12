"""
OCR Agent
---------
Converts a photo/scan of a document into plain text, using Sarvam's Document AI
(digitise) API. This is an async job API -- submit, poll until done, then
download a ZIP and pull the text file out of it. More steps than our chat-based
agents, but that's a real constraint of this API, not something we're overcomplicating.
"""
import io
import time
import zipfile

import requests

from app.llm_client import client  # reuses the same SarvamAI client instance

TERMINAL_STATES = {"completed", "partially_completed", "failed", "rejected"}


def _extract_markdown_from_zip(zip_bytes: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        md_files = [name for name in archive.namelist() if name.endswith(".md")]
        if not md_files:
            raise RuntimeError(f"No .md file in OCR result. Contents: {archive.namelist()}")
        with archive.open(md_files[0]) as f:
            return f.read().decode("utf-8")


def run_ocr(image_path: str, language: str = "en-IN") -> str:
    with open(image_path, "rb") as f:
        job = client.doc_ai.digitise(
            file=[(image_path, f, "image/png")],
            language=language,
            output_format="md",
        )

    status = job
    while status.status.lower() not in TERMINAL_STATES:
        time.sleep(3)
        status = client.doc_ai.get_status(job_id=job.job_id)

    if status.status.lower() not in ("completed", "partially_completed"):
        raise RuntimeError(f"OCR job did not succeed: status={status.status}")

    download = client.doc_ai.get_download_url(job_id=job.job_id)
    zip_response = requests.get(download.url)
    zip_response.raise_for_status()

    return _extract_markdown_from_zip(zip_response.content)


if __name__ == "__main__":
    text = run_ocr("data/sample_patient_01/doctor_notes_scan.png")
    print(text)