# ── Stage 1: build ──────────────────────────────────────────────────────────
FROM node:18-slim AS builder

WORKDIR /app

# Install production dependencies only
COPY package*.json .
RUN npm ci --omit=dev


# ── Stage 2: runtime ────────────────────────────────────────────────────────
FROM node:18-slim

WORKDIR /app

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
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

CMD ["node", "app.js"]
