# L7 CNOTA Dashboard — multi-stage deployment package
# Stage 1: Build React frontend
FROM node:18-bookworm-slim AS frontend
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build \
 && test -f dist/index.html

# Stage 2: Python runtime (HF Spaces: UID 1000, port 7860)
FROM python:3.11-slim-bookworm

RUN useradd -m -u 1000 user \
 && mkdir -p /app \
 && chown -R user:user /app

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/backend

WORKDIR /app

# Install Python deps as non-root (HF Spaces convention)
COPY --chown=user:user backend/requirements.txt /app/backend/requirements.txt
USER user
RUN pip install --no-cache-dir --user -r /app/backend/requirements.txt

# App sources + built SPA
COPY --chown=user:user --from=frontend /app/dist /app/frontend/dist
COPY --chown=user:user backend/ /app/backend/

EXPOSE 7860

# Health for orchestrators (optional)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/api/health', timeout=3)" || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--app-dir", "/app/backend"]
