# Stage 1: Build React frontend
FROM node:18 AS frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python runtime
FROM python:3.11-slim

# HF Spaces requires UID 1000
RUN useradd -m -u 1000 user
USER user:1000

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy frontend build artifacts
COPY --chown=user:user --from=frontend /app/dist ./frontend/dist

# Copy backend source
COPY --chown=user:user backend/ ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir --user -r /app/backend/requirements.txt

# HF Spaces requires port 7860
EXPOSE 7860

CMD ["python", "backend/main.py", "--host", "0.0.0.0", "--port", "7860"]
