import tempfile, os

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.pipeline import pipeline
from app.agents.ocr_agent import run_ocr

app = FastAPI(title="Discharge Summary Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://discharge-summary-generator-ten.vercel.app",
        "https://discharge-summary-generator-4gic1m9s2-om-khatavkar.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


class DischargeRequest(BaseModel):
    doctor_notes_raw: str
    lab_report_raw: str
    prescription_raw: str


class DischargeResponse(BaseModel):
    discharge_summary: str
    conflicts: list
    extracted_data: dict


@app.post("/discharge-summary", response_model=DischargeResponse)
def generate_discharge_summary(request: DischargeRequest):
    initial_state = request.model_dump()
    final_state = pipeline.invoke(initial_state)
    return DischargeResponse(
        discharge_summary=final_state["discharge_summary"],
        conflicts=final_state["conflicts"],
        extracted_data=final_state["extracted_data"],
    )


async def _ocr_upload(upload: UploadFile) -> str:
    contents = await upload.read()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    try:
        return run_ocr(tmp_path)
    finally:
        os.unlink(tmp_path)


@app.post("/discharge-summary-from-images", response_model=DischargeResponse)
async def generate_from_images(
    doctor_notes_image: UploadFile = File(...),
    lab_report_image: UploadFile = File(...),
    prescription_image: UploadFile = File(...),
):
    initial_state = {
        "doctor_notes_raw": await _ocr_upload(doctor_notes_image),
        "lab_report_raw": await _ocr_upload(lab_report_image),
        "prescription_raw": await _ocr_upload(prescription_image),
    }
    final_state = pipeline.invoke(initial_state)
    return DischargeResponse(
        discharge_summary=final_state["discharge_summary"],
        conflicts=final_state["conflicts"],
        extracted_data=final_state["extracted_data"],
    )