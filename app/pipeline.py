"""
Discharge Summary Pipeline
----------------------------
Wires the three agents into a single LangGraph flow:
extraction -> reconciliation -> summarization
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END

from app.agents.extraction_agent import run_extraction
from app.agents.reconciliation_agent import run_reconciliation
from app.agents.summarization_agent import run_summarization


class DischargeState(TypedDict):
    doctor_notes_raw: str
    lab_report_raw: str
    prescription_raw: str
    extracted_data: Optional[dict]
    conflicts: Optional[list]
    discharge_summary: Optional[str]


builder = StateGraph(DischargeState)
builder.add_node("extract", run_extraction)
builder.add_node("reconcile", run_reconciliation)
builder.add_node("summarize", run_summarization)

builder.add_edge(START, "extract")
builder.add_edge("extract", "reconcile")
builder.add_edge("reconcile", "summarize")
builder.add_edge("summarize", END)

pipeline = builder.compile()


if __name__ == "__main__":
    from pathlib import Path

    folder = Path("data/sample_patient_01")
    initial_state = {
        "doctor_notes_raw": (folder / "doctor_notes.txt").read_text(),
        "lab_report_raw": (folder / "lab_report.txt").read_text(),
        "prescription_raw": (folder / "prescription.txt").read_text(),
    }

    final_state = pipeline.invoke(initial_state)

    print("=" * 60)
    print("DISCHARGE SUMMARY")
    print("=" * 60)
    print(final_state["discharge_summary"])
    print(f"\n({len(final_state['conflicts'])} conflict(s) flagged)")