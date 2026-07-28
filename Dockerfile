# ═══════════════════════════════════════════════════════════════════
# Fake News Detector — Multi-stage Docker Build (React + FastAPI)
# ═══════════════════════════════════════════════════════════════════

# Stage 1: Build Frontend (React + Vite)
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


# Stage 2: Python Builder — install dependencies
FROM python:3.12-slim AS python-builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Download NLP models/data
RUN python -m spacy download en_core_web_sm
RUN python -c "import nltk; nltk.download('stopwords', download_dir='/install/nltk_data'); nltk.download('punkt', download_dir='/install/nltk_data'); nltk.download('punkt_tab', download_dir='/install/nltk_data')"


# Stage 3: Runtime — lean production image
FROM python:3.12-slim AS runtime

RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy installed Python packages & NLTK data
COPY --from=python-builder /install /usr/local
COPY --from=python-builder /install/nltk_data /usr/share/nltk_data

# Copy built React frontend assets
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Copy application code
COPY src/ ./src/
COPY api.py .
COPY pyproject.toml .
COPY params.yaml .
COPY metrics.json .
COPY .env.example .

# Copy trained models
COPY models/ ./models/

# Copy report figures
COPY reports/ ./reports/

# Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Create directories for runtime data
RUN mkdir -p /app/database /app/data/raw /app/data/processed /app/data/features \
    && chown -R appuser:appuser /app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NLTK_DATA=/usr/share/nltk_data \
    PORT=8000

# Expose API/App port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/docs')" || exit 1

USER appuser

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
