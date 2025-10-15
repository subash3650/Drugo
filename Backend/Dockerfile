FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/cache/huggingface \
    TRANSFORMERS_NO_ADVISORY_WARNINGS=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    ca-certificates \
    libsndfile1 \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip setuptools wheel \
 && pip --no-cache-dir install -r requirements.txt \
 && pip --no-cache-dir install --index-url https://download.pytorch.org/whl/cpu torch==2.2.0

COPY . .
RUN useradd --create-home --shell /bin/bash appuser \
 && chown -R appuser:appuser /app /cache || true

USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}"
EXPOSE 5000
ENV FLASK_ENV=production \
    HOST=0.0.0.0 \
    PORT=5000 \
    MONGO_URI=mongodb://mongo:27017/drug_detect \
    DEBUG_NLP=0
CMD ["python", "app.py"]
