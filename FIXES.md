# Fixes

## Misconfigurations

- **`api/main.py`, line 14** — `r.hset(f"job:{job_id}", "status", "queued")` used the deprecated 3-argument signature which throws a `TypeError` in redis-py v4+. Changed to `r.hset(f"job:{job_id}", mapping={"status": "queued"})`.
- **`api/.env.example`** — Missing `REDIS_HOST` and `REDIS_PORT` placeholder variables. The API requires both at runtime but they were absent from the example file. Added `REDIS_HOST=` and `REDIS_PORT=6379`.
- **`frontend/.env.example`** — Missing `PORT` placeholder. The frontend port was hardcoded to `3000` with no way to override it via environment. Added `PORT=3000` and updated `app.js` to read from `process.env.PORT`.

## Bad Practices

- **No `.gitignore` in repo** — Unwanted files and folders like `__pycache__` and `node_modules` could be committed to GitHub. Added `.gitignore` covering `__pycache__`, `node_modules`, `.env`, and `.env.local`.
- **`.env` file existed in the repository** — Credentials were committed to version control. Removed `.env` and added it to `.gitignore`. Added `.env.example` files with placeholder values instead.
- **`api/requirements.txt`, line 2** — `uvicorn` was listed without the `[standard]` extras, which omits production-grade dependencies like `uvloop` and `httptools`. Changed to `uvicorn[standard]`.
- **`api/requirements.txt` and `worker/requirements.txt`** — `redis` had no version pin, allowing silent installation of incompatible versions. Pinned to `redis>=4.0.0` in both files.
- **`frontend/app.js`, lines 12 and 20** — `req` parameter was declared but never used in both route handlers, causing ESLint errors. Renamed to `_req` to signal intentional non-use; fixed the `req.params.id` reference in `/status/:id` to use `_req.params.id`.
- **`frontend/package.json`** — No `engines` field, allowing the app to run on incompatible Node versions. Added `"engines": { "node": ">=18.0.0" }`.

## Missing Production Requirements

- **`api/main.py`** — No `/health` endpoint. Required for Docker `HEALTHCHECK` and `depends_on: condition: service_healthy` in Compose. Added `GET /health` that calls `r.ping()` and returns `{"status": "ok"}`.
- **`frontend/app.js`** — No `/health` endpoint. Same requirement as the API. Added `GET /health` returning `{"status": "ok"}`.
- **`api/main.py` and `worker/worker.py`** — Redis connection was created at module load with no retry logic. In a container environment the process would crash immediately if Redis wasn't ready. Wrapped connection in a `connect_redis()` function that retries up to 10 times with a 2-second delay before raising.
- **`worker/worker.py`** — No graceful shutdown handler. Docker sends `SIGTERM` on container stop; without a handler the worker would be killed mid-job. Added `SIGTERM` and `SIGINT` handlers that set a `shutdown` flag, allowing the current job to finish before the process exits.
- **`worker/worker.py`, line 17** — `r.hset(f"job:{job_id}", "status", "completed")` had the same redis-py v4+ incompatibility as the API. Changed to `r.hset(f"job:{job_id}", mapping={"status": "completed"})`.
