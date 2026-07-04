import { DiagnosisReport } from "@/lib/api";
import { diagnosisColor } from "@/lib/diagnosisColor";
import ModelCard from "./ModelCard";

export default function DiagnosisPanel({ report }: { report: DiagnosisReport }) {
  const color = diagnosisColor(report.primary_diagnosis);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <span className="font-mono text-xs uppercase tracking-widest text-muted">
          Primary diagnosis · decided by {report.decision_method.replace(/_/g, " ")}
        </span>
        <h2 className="font-display text-4xl font-bold" style={{ color }}>
          {report.primary_diagnosis}
        </h2>
        <span className="font-mono text-sm text-muted">Confidence: {report.confidence}</span>
        {!report.llm_used && (
          <div className="mt-2 inline-block border border-ischemia/40 px-2 py-1 font-mono text-[11px] text-ischemia">
            LLM explanation offline — showing deterministic result only
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {report.per_model.map((res) => (
          <ModelCard key={res.model} result={res} />
        ))}
      </div>

      <div className="space-y-4 border border-hairline bg-panel2 p-4">
        <div>
          <h3 className="mb-1 font-mono text-xs uppercase tracking-widest text-cyan">Model consensus</h3>
          <p className="text-sm leading-relaxed text-ink/90">{report.model_consensus}</p>
        </div>
        <div>
          <h3 className="mb-1 font-mono text-xs uppercase tracking-widest text-cyan">Clinical notes</h3>
          <p className="text-sm leading-relaxed text-ink/90">{report.doctor_notes}</p>
        </div>
        <div>
          <h3 className="mb-1 font-mono text-xs uppercase tracking-widest text-cyan">Suggested action</h3>
          <p className="text-sm leading-relaxed text-ink/90">{report.suggested_action}</p>
        </div>
      </div>

      <p className="font-mono text-[11px] text-muted">
        Research demo only — not a certified diagnostic device. Not for clinical use.
      </p>
    </div>
  );
}
