<div align="center">

# 🧠 Brain Stroke Agentic Diagnosis System

Multi-model CNN ensemble + Grad-CAM explainability + LLM-generated clinical reports — deployed end-to-end.

**[Live Demo →](https://brain-stroke-agent.vercel.app)** &nbsp;|&nbsp; **[API Docs →](https://sajidftw-brain-stroke-agent.hf.space/docs)**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat&logo=next.js&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?style=flat&logoColor=white)

</div>

> ⚠️ Research/demo project. Not a certified diagnostic device.

## What it does

Three CNNs (Custom CNN, ResNet18, AlexNet) independently classify a brain CT scan as **Bleeding**, **Ischemia**, or **Normal**. The diagnosis itself is decided **deterministically** — majority vote across the three models, with averaged softmax probabilities as a tiebreak. Groq is only used *after* the diagnosis is fixed, to explain it in clinical language — it can't override the result. Grad-CAM heatmaps give a visual, per-model explanation of what each network is looking at.

## Architecture

```
Next.js frontend  ──POST /predict (image)──▶  FastAPI backend
                                                  ├─ 3× CNN inference + Grad-CAM
                                                  ├─ deterministic consensus vote
                                                  └─ Groq: explain the fixed result
                   ◀──── diagnosis + heatmaps + report ────
```

- **Backend** — FastAPI, PyTorch, OpenCV (Grad-CAM), Groq. Containerized, deployed on **Hugging Face Spaces**.
- **Frontend** — Next.js console UI with a live "scan viewport." Deployed on **Vercel**.
- **CI/CD** — GitHub Actions: lint + build on every push, auto-publish to **Docker Hub**, auto-deploy backend to **Hugging Face Spaces**.

## Tech stack

`Python` `PyTorch` `FastAPI` `OpenCV` `Groq` `Next.js` `TypeScript` `Tailwind` `Docker` `GitHub Actions` `Hugging Face Spaces` `Vercel`

## Run it locally

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`. Model weights (`cnn_model.pth`, `resnet18_model.pth`, `alexnet_model.pth`) go in `backend/model_weights/` — tracked via Git LFS.

## API

`POST /predict` — multipart form, field `file` (PNG/JPEG):

```json
{
  "primary_diagnosis": "Ischemia",
  "confidence": "High (Unanimous)",
  "decision_method": "majority_vote",
  "model_consensus": "...",
  "doctor_notes": "...",
  "suggested_action": "...",
  "per_model": [{ "model": "CNN", "prediction": "Ischemia", "probabilities": {}, "xai_image_base64": "..." }],
  "llm_used": true
}
```
