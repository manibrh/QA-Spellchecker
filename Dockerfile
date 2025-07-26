# =====================
# Dockerfile (Flask + Gunicorn)
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

# Copy source code
COPY . .

# Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 10000

# Gunicorn command for Flask (WSGI app)
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:10000", "app:app"]
