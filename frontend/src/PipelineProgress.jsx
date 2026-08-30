import { useEffect, useState } from 'react'

const STAGES = [
  { key: 'extract', label: 'Extracting patient data' },
  { key: 'reconcile', label: 'Checking for medication conflicts' },
  { key: 'summarize', label: 'Writing discharge summary' },
]

export default function PipelineProgress({ loading }) {
  const [activeIndex, setActiveIndex] = useState(-1)

  useEffect(() => {
    if (!loading) {
      setActiveIndex(-1)
      return
    }
    setActiveIndex(0)
    const timers = [
      setTimeout(() => setActiveIndex(1), 2500),
      setTimeout(() => setActiveIndex(2), 4000),
    ]
    return () => timers.forEach(clearTimeout)
  }, [loading])

  if (!loading) return null

  return (
    <div className="flex items-center gap-3 font-mono text-xs">
      {STAGES.map((stage, i) => {
        const isDone = i < activeIndex
        const isActive = i === activeIndex
        return (
          <div key={stage.key} className="flex items-center gap-2">
            <span
              className={`w-2.5 h-2.5 rounded-full border ${
                isDone ? "bg-clinical border-clinical" :
                isActive ? "bg-gold border-gold animate-pulse" :
                "bg-transparent border-rule"
              }`}
            />
            <span className={isActive ? "text-ink" : "text-ink/40"}>{stage.label}</span>
            {i < STAGES.length - 1 && <span className="text-rule">—</span>}
          </div>
        )
      })}
    </div>
  )
}