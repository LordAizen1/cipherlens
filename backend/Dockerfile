# ── Build stage ───────────────────────────────────────────────
FROM python:3.12 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ─────────────────────────────────────────────
FROM python:3.12
WORKDIR /app

# The full image already has most libraries, but we'll keep libgomp1 just in case
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY . .

# Use a direct uvicorn call without sh -c to avoid variable expansion issues
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
