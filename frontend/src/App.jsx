import { useState } from 'react'
import { generateDischargeSummary, generateDischargeSummaryFromImages } from './api'
import PipelineProgress from './PipelineProgress'
import ResultsDisplay from './ResultsDisplay'

const SAMPLE_DOCTOR_NOTES = `[SYNTHETIC TEST DATA - NOT A REAL PATIENT]

Patient: Jane Doe
MRN: TEST-00123
DOB: 14-Mar-1958
Admission Date: 10-Aug-2026
Discharge Date: 15-Aug-2026

Admitting Diagnosis: Community-acquired pneumonia, right lower lobe
Secondary Diagnosis: Acute-on-chronic kidney injury, CKD Stage 3b

History: 68F with known CKD stage 3b presented with 3 days of fever,
productive cough, and dyspnea. Chest X-ray confirmed RLL consolidation.
Treated with IV antibiotics and supportive care. Baseline creatinine 1.6 mg/dL.

Discharge Condition: Afebrile x 48h, O2 sat 96% on room air, tolerating oral intake.
Follow-up: Nephrology in 2 weeks, PCP in 1 week.`

const SAMPLE_LAB_REPORT = `[SYNTHETIC TEST DATA - NOT A REAL PATIENT]

Patient: Jane Doe   MRN: TEST-00123
Collected: 14-Aug-2026 06:30

Potassium: 5.2 mmol/L (HIGH - normal 3.5-5.0)
Creatinine: 2.1 mg/dL (HIGH - normal 0.6-1.2)
eGFR: 27 mL/min/1.73m2 (LOW - Stage 4 CKD range)
BUN: 42 mg/dL (HIGH)
Hemoglobin: 11.2 g/dL (LOW)

Impression: Worsening renal function since baseline (Cr 1.6 -> 2.1).
Recommend renal dosing review for all current medications.`

const SAMPLE_PRESCRIPTION = `[SYNTHETIC TEST DATA - NOT A REAL PATIENT]

Patient: Jane Doe   MRN: TEST-00123
Discharge Prescriptions:
1. Vancomycin 1g IV q8h - continue x2 days via home infusion
2. Lisinopril 10mg PO once daily
3. Metformin 1000mg PO twice daily
4. Acetaminophen 500mg PO q6h PRN pain`

function FileSlot({ label, file, onChange }) {
  return (
    <label className="flex flex-col gap-1 border border-rule rounded-lg p-4 cursor-pointer hover:border-clinical transition-colors flex-1">
      <span className="font-sans text-sm font-semibold text-clinical">{label}</span>
      <span className="font-mono text-xs text-ink/60 truncate">
        {file ? file.name : "Click to choose a photo"}
      </span>
      <input
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => onChange(e.target.files[0])}
      />
    </label>
  )
}

function App() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const [doctorNotesImage, setDoctorNotesImage] = useState(null)
  const [labReportImage, setLabReportImage] = useState(null)
  const [prescriptionImage, setPrescriptionImage] = useState(null)

  async function handleGenerate() {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await generateDischargeSummary({
        doctor_notes_raw: SAMPLE_DOCTOR_NOTES,
        lab_report_raw: SAMPLE_LAB_REPORT,
        prescription_raw: SAMPLE_PRESCRIPTION,
      })
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleGenerateFromImages() {
    if (!doctorNotesImage || !labReportImage || !prescriptionImage) {
      setError("Please choose all three photos before generating.")
      return
    }
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await generateDischargeSummaryFromImages({
        doctorNotes: doctorNotesImage,
        labReport: labReportImage,
        prescription: prescriptionImage,
      })
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center gap-6 p-10">
      <h1 className="font-serif text-4xl text-clinical">Discharge Summary Generator</h1>

      <button
        onClick={handleGenerate}
        disabled={loading}
        className="font-sans bg-clinical text-paper px-6 py-3 rounded disabled:opacity-50"
      >
        {loading ? "Generating..." : "Generate Discharge Summary (Sample Data)"}
      </button>

      <div className="flex items-center gap-3 w-full max-w-3xl">
        <div className="flex-1 border-t border-rule" />
        <span className="font-mono text-xs text-ink/50 uppercase">or upload your own</span>
        <div className="flex-1 border-t border-rule" />
      </div>

      <div className="flex flex-col sm:flex-row gap-3 w-full max-w-3xl">
        <FileSlot label="Doctor's Notes" file={doctorNotesImage} onChange={setDoctorNotesImage} />
        <FileSlot label="Lab Report" file={labReportImage} onChange={setLabReportImage} />
        <FileSlot label="Prescription" file={prescriptionImage} onChange={setPrescriptionImage} />
      </div>

      <button
        onClick={handleGenerateFromImages}
        disabled={loading}
        className="font-sans bg-gold text-paper px-6 py-3 rounded disabled:opacity-50"
      >
        {loading ? "Generating..." : "Generate from Photos"}
      </button>

      <PipelineProgress loading={loading} />

      {error && <p className="font-mono text-flag">{error}</p>}

      {result && <ResultsDisplay result={result} />}
    </div>
  )
}

export default App