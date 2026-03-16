FROM python:3.11-bookworm

WORKDIR /app

# Context is repo root when Railway builds, so paths are relative to root
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
