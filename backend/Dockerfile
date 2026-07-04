# CPU-only image. Hugging Face Spaces' free/basic tier is CPU, and torch+torchvision
# CPU wheels keep the image far smaller than the CUDA build.
FROM python:3.11-slim

# opencv needs these system libs even in "headless" mode
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY model_weights ./model_weights

# Hugging Face Spaces (Docker SDK) always sends traffic to port 7860.
# Locally you can still map any host port to this container port.
ENV MODEL_DIR=/app/model_weights
ENV PORT=7860
EXPOSE 7860

# Hugging Face Spaces containers run as a non-root user by convention.
RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
