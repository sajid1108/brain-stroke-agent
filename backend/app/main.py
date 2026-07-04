import io
import logging
import os

import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from .agent import AgenticDoctor
from .consensus import compute_consensus_diagnosis
from .gradcam import generate_gradcam, overlay_cam_on_image_b64
from .models import CLASS_NAMES, DEVICE, get_target_layer, load_models, val_transform
from .schemas import DiagnosisReport, HealthResponse, ModelPrediction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("brain_stroke_agent")

MODEL_DIR = os.environ.get("MODEL_DIR", "/app/model_weights")
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI(
    title="Brain Stroke Agentic Diagnosis API",
    description=(
        "Multi-model CNN ensemble (Custom CNN, ResNet18, AlexNet) cross-validates brain stroke "
        "detection on CT scans. Grad-CAM (XAI) generates heatmaps. The diagnosis is decided "
        "deterministically (majority vote + probability-average tiebreak); Groq only explains it."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_models = None
_doctor = None


@app.on_event("startup")
def startup_event():
    global _models, _doctor
    try:
        _models = load_models(MODEL_DIR)
    except FileNotFoundError as exc:
        logger.error("Model weights not found: %s", exc)
        _models = None
    _doctor = AgenticDoctor()


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        models_loaded=_models is not None,
        groq_configured=_doctor.enabled if _doctor else False,
    )


@app.post("/predict", response_model=DiagnosisReport)
async def predict(file: UploadFile = File(...)):
    if _models is None:
        raise HTTPException(
            status_code=503,
            detail="Model weights not loaded on the server. Check MODEL_DIR / deployment logs.",
        )
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image (PNG/JPEG).")

    raw = await file.read()
    try:
        pil_image = Image.open(io.BytesIO(raw))
        pil_image.load()
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read the uploaded image.")

    img_tensor = val_transform(pil_image).unsqueeze(0).to(DEVICE)

    tool_output = []
    for model_name, model in _models.items():
        target_layer = get_target_layer(model, model_name)
        cam, pred_idx, probs = generate_gradcam(model, img_tensor, target_layer)
        pred_label = CLASS_NAMES[pred_idx]
        xai_b64 = overlay_cam_on_image_b64(pil_image, cam)

        tool_output.append(
            {
                "model": model_name,
                "prediction": pred_label,
                "probabilities": {cls: float(p) for cls, p in zip(CLASS_NAMES, probs)},
                "xai_image_base64": xai_b64,
            }
        )

    decision = compute_consensus_diagnosis(tool_output)
    explanation = _doctor.explain(tool_output, decision)

    return DiagnosisReport(
        primary_diagnosis=explanation["primary_diagnosis"],
        confidence=explanation["confidence"],
        decision_method=explanation["decision_method"],
        model_consensus=explanation["model_consensus"],
        doctor_notes=explanation["doctor_notes"],
        suggested_action=explanation["suggested_action"],
        per_model=[ModelPrediction(**res) for res in tool_output],
        llm_used=explanation["llm_used"],
    )
