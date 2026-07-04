import { ModelPrediction } from "@/lib/api";
import { diagnosisColor } from "@/lib/diagnosisColor";

export default function ModelCard({ result }: { result: ModelPrediction }) {
  const color = diagnosisColor(result.prediction);
  const topProb = Math.max(...Object.values(result.probabilities));

  return (
    <div className="border border-hairline bg-panel p-3">
      <div className="mb-2 flex items-center justify-between">
        <span className="font-display text-sm text-ink">{result.model}</span>
        <span className="font-mono text-xs" style={{ color }}>
          {result.prediction}
        </span>
      </div>

      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={`data:image/png;base64,${result.xai_image_base64}`}
        alt={`${result.model} Grad-CAM heatmap`}
        className="mb-2 aspect-square w-full rounded-sm object-cover"
      />

      <div className="space-y-1">
        {Object.entries(result.probabilities)
          .sort((a, b) => b[1] - a[1])
          .map(([cls, prob]) => (
            <div key={cls} className="flex items-center gap-2 font-mono text-[11px] text-muted">
              <span className="w-16 shrink-0 truncate">{cls}</span>
              <div className="h-1 flex-1 bg-hairline">
                <div
                  className="h-1"
                  style={{
                    width: `${prob * 100}%`,
                    backgroundColor: prob === topProb ? color : "#3A4552",
                  }}
                />
              </div>
              <span className="w-10 shrink-0 text-right">{(prob * 100).toFixed(0)}%</span>
            </div>
          ))}
      </div>
    </div>
  );
}
