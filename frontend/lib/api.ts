export interface ModelPrediction {
  model: string;
  prediction: string;
  probabilities: Record<string, number>;
  xai_image_base64: string;
}

export interface DiagnosisReport {
  primary_diagnosis: string;
  confidence: string;
  decision_method: string;
  model_consensus: string;
  doctor_notes: string;
  suggested_action: string;
  per_model: ModelPrediction[];
  llm_used: boolean;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function runDiagnosis(file: File): Promise<DiagnosisReport> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/predict`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail?.detail || `Request failed with status ${res.status}`);
  }

  return res.json();
}
