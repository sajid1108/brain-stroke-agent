# Brain Stroke Agentic Diagnosis System

Multi-model CNN ensemble (Custom CNN, ResNet18, AlexNet) cross-validates brain stroke
detection on CT scans. Grad-CAM (XAI) generates heatmaps. The diagnosis is decided
**deterministically** (majority vote + probability-average tiebreak); Groq is used only
to **explain** that already-decided result in clinical language.

```
brain-stroke-agent/
├── backend/                # FastAPI service
│   ├── app/                # main.py, models.py, gradcam.py, consensus.py, agent.py
│   ├── model_weights/      # put your 3 .pth files here (git-lfs tracked)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # Next.js console UI
├── .github/workflows/       # CI + Hugging Face Space auto-deploy
└── README.md
```

> ⚠️ Research/demo project. Not a certified diagnostic device.

---

## Step 1 — Add your model weights

Copy your 3 trained files into `backend/model_weights/`, named exactly:

```
cnn_model.pth
resnet18_model.pth
alexnet_model.pth
```

These are large binary files, so they're tracked with **Git LFS** (see `.gitattributes`).
Install LFS once per machine, then per clone:

```bash
git lfs install
```

---

## Step 2 — Run the backend locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then edit .env and paste your real GROQ_API_KEY
export $(cat .env | xargs)  # or just use a tool like `direnv`/`python-dotenv`
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` — try `/health`, then `/predict` with a CT image.
Without `GROQ_API_KEY` set, `/predict` still works; it just returns a fallback note
instead of the LLM's clinical write-up.

---

## Step 3 — Run the frontend locally

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm run dev
```

Open `http://localhost:3000`, drop in a CT scan, click **Run diagnosis**.

---

## Step 4 — Build & run the backend with Docker

```bash
cd backend
docker build -t brain-stroke-agent-backend .
docker run -p 8000:7860 -e GROQ_API_KEY=your_key_here brain-stroke-agent-backend
```

API is now on `http://localhost:8000` (container listens on 7860 internally — that's
the port Hugging Face Spaces expects).

---

## Step 5 — Push to GitHub

```bash
cd brain-stroke-agent
git init
git lfs install
git lfs track "*.pth"     # already in .gitattributes, this just confirms it's active
git add .
git commit -m "Initial commit: backend + frontend + docker + CI"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

---

## Step 6 — GitHub Actions (CI)

`.github/workflows/ci.yml` runs automatically on every push/PR to `main`:
- Backend: lint (`ruff`) + byte-compile check
- Frontend: `next lint` + `next build`
- Docker: builds the backend image (with dummy weight files, just to prove it builds)

Nothing to configure — it just needs the code pushed.

### Docker Hub publish (`docker-publish.yml`)

Builds `backend/` and pushes `sajid1108/brain-stroke-agent-backend:latest` +
`:<commit-sha>` to Docker Hub on every push to `main`. Requires two repo secrets:
- `DOCKERHUB_USERNAME` = `sajid1108`
- `DOCKERHUB_TOKEN` = a Docker Hub access token (hub.docker.com → Account Settings →
  Security → New Access Token — not your password)

---

## Step 7 — Deploy the backend to Hugging Face Spaces

1. On huggingface.co: **New Space** → SDK: **Docker** → name it (e.g. `brain-stroke-agent`).
2. In the Space's **Settings → Repository secrets**, add `GROQ_API_KEY`.
3. Back in your **GitHub repo settings → Secrets and variables → Actions**, add:
   - `HF_TOKEN` — a Hugging Face token with **write** access (huggingface.co/settings/tokens)
   - `HF_SPACE_REPO` — e.g. `your-hf-username/brain-stroke-agent`
4. Push to `main` (or run the workflow manually from the Actions tab). The
   `deploy-backend-hf.yml` workflow syncs `backend/` into the Space and pushes it —
   Hugging Face then builds the Dockerfile and serves it at
   `https://<your-hf-username>-brain-stroke-agent.hf.space`.

**First-time alternative (no GitHub Action needed):** you can also push directly:
```bash
git clone https://huggingface.co/spaces/<your-hf-username>/brain-stroke-agent /tmp/space
rsync -a --exclude='.git' backend/ /tmp/space/
cp backend/README_SPACE.md /tmp/space/README.md
cd /tmp/space && git lfs track "*.pth" && git add . && git commit -m "init" && git push
```

---

## Step 8 — Deploy the frontend to Vercel

1. On vercel.com: **New Project** → import your GitHub repo.
2. Set **Root Directory** to `frontend`.
3. Add environment variable: `NEXT_PUBLIC_API_BASE_URL` = your HF Space URL
   (e.g. `https://your-hf-username-brain-stroke-agent.hf.space`).
4. Deploy. Vercel auto-redeploys on every push to `main`.
5. Back in the backend's `.env` / HF Space secret, set `ALLOWED_ORIGINS` to your
   Vercel domain so CORS allows the browser to call the API.

---

## API contract

`POST /predict` — multipart form, field `file` (PNG/JPEG) → `DiagnosisReport` JSON:
```json
{
  "primary_diagnosis": "Ischemia",
  "confidence": "High (Unanimous)",
  "decision_method": "majority_vote",
  "model_consensus": "...",
  "doctor_notes": "...",
  "suggested_action": "...",
  "per_model": [{"model": "CNN", "prediction": "Ischemia", "probabilities": {...}, "xai_image_base64": "..."}],
  "llm_used": true
}
```
