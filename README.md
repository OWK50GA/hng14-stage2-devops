# Job Processor

A containerized job processing system consisting of four services: a Node.js frontend, a Python/FastAPI backend, a Python worker, and Redis as the message queue.

Users submit jobs through the web dashboard. The API queues them in Redis. The worker picks them up, processes them, and marks them complete. The frontend polls for status updates in real time.

## Architecture

```
Browser → Frontend (Node.js :3000) → API (FastAPI :8000) → Redis
                                                               ↑
                                                          Worker (Python)
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) v24+
- [Docker Compose](https://docs.docker.com/compose/install/) v2.20+ (included with Docker Desktop)
- Git

Verify your installation:

```bash
docker --version
docker compose version
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in the required values:

```
REDIS_PASSWORD=your_secure_password_here
REDIS_HOST=redis
REDIS_PORT=6379
API_URL=http://api:8000
FRONTEND_PORT=3000
APP_ENV=production
```

> `REDIS_HOST` must be `redis` — that is the service name Docker Compose uses for internal DNS resolution.

### 3. Build and start the stack

```bash
docker compose up --build
```

To run in the background:

```bash
docker compose up --build -d
```

### 4. Open the dashboard

Navigate to [http://localhost:3000](http://localhost:3000) in your browser.

## What a Successful Startup Looks Like

When all services are healthy you will see output similar to this:

```
redis-1     | Ready to accept connections
api-1       | INFO:     Application startup complete.
api-1       | INFO:     Uvicorn running on http://0.0.0.0:8000
worker-1    | Redis connected
frontend-1  | Frontend running on port 3000
```

You can verify all containers are healthy:

```bash
docker compose ps
```

Expected output:

```
NAME                    STATUS
your-repo-redis-1       Up (healthy)
your-repo-api-1         Up (healthy)
your-repo-worker-1      Up (healthy)
your-repo-frontend-1    Up (healthy)
```

All four services should show `(healthy)` — not just `Up`.

## Verifying the Application Works

1. Open [http://localhost:3000](http://localhost:3000)
2. Click **Submit New Job**
3. A job ID appears and its status shows `queued`
4. Within a few seconds the status updates to `completed`

You can also test via the API directly:

```bash
# Submit a job
curl -X POST http://localhost:8000/jobs

# Check job status (replace <job_id> with the returned ID)
curl http://localhost:8000/jobs/<job_id>

# Health check
curl http://localhost:8000/health
```

## Stopping the Stack

```bash
docker compose down
```

To also remove volumes:

```bash
docker compose down -v
```

## Environment Variables Reference

| Variable | Description | Default |
|---|---|---|
| `REDIS_PASSWORD` | Password for Redis authentication | required |
| `REDIS_HOST` | Redis hostname (use `redis` for compose) | required |
| `REDIS_PORT` | Redis port | `6379` |
| `API_URL` | URL the frontend uses to reach the API | required |
| `FRONTEND_PORT` | Host port to expose the frontend on | `3000` |
| `APP_ENV` | Application environment | `production` |

## CI/CD Pipeline

The GitHub Actions pipeline runs automatically on every push and pull request:

```
lint → test → build → security scan → integration test → deploy
```

| Stage | What it does |
|---|---|
| lint | flake8 (Python), eslint (JavaScript), hadolint (Dockerfiles) |
| test | pytest with mocked Redis, uploads coverage report as artifact |
| build | Builds all three images, tags with git SHA and `latest`, pushes to local registry |
| security | Trivy scan on all images, fails on CRITICAL findings, uploads SARIF artifact |
| integration | Brings full stack up, submits a real job, polls until completed, tears down |
| deploy | Rolling update to production server — only on pushes to `main` |

### Required GitHub Secrets (for deploy stage)

| Secret | Description |
|---|---|
| `DEPLOY_HOST` | IP address or hostname of your server |
| `DEPLOY_USER` | SSH username |
| `DEPLOY_KEY` | Full contents of your private SSH key |
| `REDIS_PASSWORD` | Redis password used on the production server |
