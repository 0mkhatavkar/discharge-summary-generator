from pydantic import BaseModel
from typing import Optional

class DischargeState(BaseModel):
    doctor_notes_raw: str = ""
    lab_report_raw: str = ""
    prescription_raw: str = ""
    extracted_data: Optional[dict] = None
    conflicts: Optional[list] = None
    discharge_summary: Optional[str] = None