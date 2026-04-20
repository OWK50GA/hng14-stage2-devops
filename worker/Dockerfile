# ── Stage 1: build ──────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source (no .env files — config comes from env vars at runtime)
COPY worker.py .

# Run as non-root user
RUN useradd --no-create-home --shell /bin/false appuser
USER appuser

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import redis, os; r = redis.Redis(host=os.environ['REDIS_HOST'], port=int(os.environ.get('REDIS_PORT', 6379)), password=os.environ['REDIS_PASSWORD']); r.ping()"

CMD ["python", "worker.py"]
