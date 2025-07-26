# =====================
# Dockerfile (Optimized)
# =====================
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev && \
    rm -rf /var/lib/apt/lists/*

COPY . .

# Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 10000

# Gunicorn with Uvicorn worker, 2-4 workers, 120s timeout
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--timeout", "120", "-b", "0.0.0.0:10000", "app:app"]
