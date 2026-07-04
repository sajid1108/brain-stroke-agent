from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class ModelPrediction(BaseModel):
    model: str
    prediction: str
    probabilities: Dict[str, float]
    xai_image_base64: str  # Grad-CAM heatmap overlay, PNG, base64-encoded


class ConsensusResult(BaseModel):
    primary_diagnosis: str
    confidence: str
    decision_method: str
    vote_counts: Dict[str, int]
    average_probabilities: Dict[str, float]


class DiagnosisReport(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    primary_diagnosis: str
    confidence: str
    decision_method: str
    model_consensus: str
    doctor_notes: str
    suggested_action: str
    per_model: List[ModelPrediction]
    llm_used: bool  # False if GROQ_API_KEY missing -> deterministic-only fallback


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    groq_configured: bool
