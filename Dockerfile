FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
 && pip install --prefer-binary -r requirements.txt
COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

