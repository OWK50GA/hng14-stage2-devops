#!/usr/bin/env bash
set -euo pipefail

FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
TIMEOUT="${TIMEOUT:-60}"

echo "Waiting for frontend to be healthy..."
ELAPSED=0
until curl -sf "$FRONTEND_URL/health" > /dev/null; do
  if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
    echo "ERROR: Frontend did not become healthy within ${TIMEOUT}s"
    exit 1
  fi
  sleep 2
  ELAPSED=$((ELAPSED + 2))
done
echo "Frontend is healthy"

echo "Submitting a job..."
JOB_ID=$(curl -sf -X POST "$FRONTEND_URL/submit" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
echo "Submitted job: $JOB_ID"

echo "Polling for job completion (timeout: ${TIMEOUT}s)..."
ELAPSED=0
while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
  STATUS=$(curl -sf "$FRONTEND_URL/status/$JOB_ID" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
  echo "  status=$STATUS (${ELAPSED}s)"
  if [ "$STATUS" = "completed" ]; then
    echo "Job completed successfully"
    exit 0
  fi
  sleep 3
  ELAPSED=$((ELAPSED + 3))
done

echo "ERROR: Job did not complete within ${TIMEOUT}s"
exit 1
