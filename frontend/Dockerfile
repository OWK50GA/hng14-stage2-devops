# ── Stage 1: build ──────────────────────────────────────────────────────────
FROM node:18-slim AS builder

WORKDIR /app

# Install production dependencies only
COPY package*.json .
RUN npm ci --omit=dev


# ── Stage 2: runtime ────────────────────────────────────────────────────────
FROM node:18-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy installed node_modules from builder
COPY --from=builder /app/node_modules ./node_modules

# Copy application source (no .env files — config comes from env vars at runtime)
COPY app.js .
COPY views/ ./views/

# Run as non-root user
RUN adduser --disabled-password --no-create-home appuser
USER appuser

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

CMD ["node", "app.js"]
