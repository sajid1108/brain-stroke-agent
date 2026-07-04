---
title: Brain Stroke Agentic Diagnosis
emoji: 🧠
colorFrom: blue
colorTo: red
sdk: docker
app_port: 7860
pinned: false
---

# Brain Stroke Agentic Diagnosis API

FastAPI backend: 3-model CNN ensemble (CNN, ResNet18, AlexNet) + Grad-CAM + deterministic
consensus + Groq-generated clinical explanation.

- `GET /health`
- `POST /predict` (multipart form, field name `file`)
- Interactive docs at `/docs`

Set the `GROQ_API_KEY` secret in this Space's Settings for the LLM explanation step;
without it the API still returns the deterministic diagnosis with a fallback note.
