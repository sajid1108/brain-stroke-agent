"use client";

import { useState } from "react";
import ScanViewport from "@/components/ScanViewport";
import DiagnosisPanel from "@/components/DiagnosisPanel";
import { runDiagnosis, DiagnosisReport } from "@/lib/api";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [report, setReport] = useState<DiagnosisReport | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleFileSelected(selected: File) {
    setFile(selected);
    setPreviewUrl(URL.createObjectURL(selected));
    setReport(null);
    setError(null);
  }

  async function handleAnalyze() {
    if (!file) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await runDiagnosis(file);
      setReport(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-void px-6 py-10 md:px-12">
      <header className="mb-10 flex items-baseline justify-between border-b border-hairline pb-4">
        <div>
          <span className="font-mono text-xs uppercase tracking-widest text-cyan">
            Agentic Diagnosis Console
          </span>
          <h1 className="font-display text-2xl font-bold text-ink">Brain Stroke CT Triage</h1>
        </div>
        <span className="font-mono text-xs text-muted">CNN · ResNet18 · AlexNet</span>
      </header>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-[380px_1fr]">
        <div className="flex flex-col gap-4">
          <ScanViewport previewUrl={previewUrl} isLoading={isLoading} onFileSelected={handleFileSelected} />
          <button
            type="button"
            disabled={!file || isLoading}
            onClick={handleAnalyze}
            className="w-full bg-cyan py-2.5 font-mono text-sm font-medium uppercase tracking-widest text-void transition-opacity disabled:cursor-not-allowed disabled:opacity-30"
          >
            {isLoading ? "Analyzing…" : "Run diagnosis"}
          </button>
          {error && <p className="font-mono text-xs text-bleeding">{error}</p>}
        </div>

        <div>
          {report ? (
            <DiagnosisPanel report={report} />
          ) : (
            <div className="flex h-full min-h-[300px] items-center justify-center border border-dashed border-hairline font-mono text-sm text-muted">
              Diagnosis output will appear here
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
