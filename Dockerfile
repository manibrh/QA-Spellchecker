# =====================
# Dockerfile
# =====================
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y gcc libglib2.0-0 libsm6 libxext6 libxrender-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 10000

CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
