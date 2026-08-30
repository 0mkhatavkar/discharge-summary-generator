function SeverityBadge({ severity }) {
  const label = severity === "high" ? "High" : "Moderate"
  return (
    <span className="font-mono text-xs uppercase tracking-wide px-2 py-0.5 rounded border border-flag text-flag whitespace-nowrap">
      {label}
    </span>
  )
}

function LabRow({ lab }) {
  const isFlagged = Boolean(lab.flag)
  return (
    <tr className="border-b border-rule last:border-0">
      <td className="py-2 pr-4 font-sans">{lab.test}</td>
      <td className={`py-2 pr-4 font-mono ${isFlagged ? "text-gold font-medium" : ""}`}>
        {lab.value} {lab.unit}
      </td>
      <td className="py-2 font-mono text-xs uppercase text-gold">{lab.flag || ""}</td>
    </tr>
  )
}

export default function ResultsDisplay({ result }) {
  const { discharge_summary, conflicts, extracted_data } = result
  const { patient_info, diagnoses, medications, lab_values, follow_up } = extracted_data

  // The narrative text has trends/flags appended as plain text (built deterministically
  // in Python). We split those off here so each part can be styled as real UI instead
  // of showing the same information twice.
  const narrative = discharge_summary.split("\n\nKey lab trends:")[0]

  return (
    <div className="w-full max-w-3xl flex flex-col gap-8 text-left">
      <div className="border-b border-rule pb-4">
        <h2 className="font-serif text-2xl text-clinical">{patient_info.name}</h2>
        <p className="font-mono text-xs text-ink/70 mt-1">
          MRN {patient_info.mrn} · DOB {patient_info.dob} · Admitted {patient_info.admission_date} · Discharged {patient_info.discharge_date}
        </p>
      </div>

      {conflicts.length > 0 && (
        <div className="border border-flag rounded-lg p-5 bg-flag/5">
          <h3 className="font-sans font-semibold text-flag uppercase text-sm tracking-wide mb-3">
            ⚠ Medication Safety Flags — Requires Clinician Review
          </h3>
          <ul className="flex flex-col gap-3">
            {conflicts.map((c, i) => (
              <li key={i} className="flex items-start justify-between gap-4">
                <div>
                  <span className="font-sans font-semibold capitalize">{c.medication}</span>
                  <p className="font-sans text-sm text-ink/80">{c.concern}</p>
                  <p className="font-mono text-xs text-ink/60 mt-1">
                    {c.lab_test} = {c.lab_value} (threshold {c.threshold})
                  </p>
                </div>
                <SeverityBadge severity={c.severity} />
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <h3 className="font-sans font-semibold text-sm uppercase tracking-wide text-clinical mb-2">Diagnoses</h3>
        <ul className="list-disc list-inside font-sans text-sm">
          {diagnoses.map((d, i) => <li key={i}>{d}</li>)}
        </ul>
      </div>

      <div>
        <h3 className="font-sans font-semibold text-sm uppercase tracking-wide text-clinical mb-2">Discharge Medications</h3>
        <table className="w-full text-sm">
          <tbody>
            {medications.map((m, i) => (
              <tr key={i} className="border-b border-rule last:border-0">
                <td className="py-2 pr-4 font-sans">{m.name}</td>
                <td className="py-2 pr-4 font-mono">{m.dose}</td>
                <td className="py-2 pr-4 font-mono text-ink/70">{m.frequency}</td>
                <td className="py-2 font-mono text-xs uppercase text-ink/50">{m.route}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div>
        <h3 className="font-sans font-semibold text-sm uppercase tracking-wide text-clinical mb-2">Key Lab Results</h3>
        <table className="w-full text-sm">
          <tbody>
            {lab_values.map((l, i) => <LabRow key={i} lab={l} />)}
          </tbody>
        </table>
      </div>

      <div>
        <h3 className="font-sans font-semibold text-sm uppercase tracking-wide text-clinical mb-2">Follow-Up Plan</h3>
        <ul className="list-disc list-inside font-sans text-sm">
          {follow_up.map((f, i) => <li key={i}>{f}</li>)}
        </ul>
      </div>

      <div className="bg-white border border-rule rounded-lg p-6 shadow-sm">
        <h3 className="font-sans font-semibold text-sm uppercase tracking-wide text-clinical mb-3">Discharge Summary</h3>
        <p className="font-serif text-base leading-relaxed whitespace-pre-line">{narrative.trim()}</p>
      </div>
    </div>
  )
}