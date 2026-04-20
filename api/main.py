from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis
import uuid
import os
import time


def connect_redis(retries=10, delay=2):
    for attempt in range(retries):
        try:
            client = redis.Redis(
                host=os.environ["REDIS_HOST"],
                port=int(os.environ.get("REDIS_PORT", 6379)),
                password=os.environ["REDIS_PASSWORD"],
            )
            client.ping()
            return client
        except redis.exceptions.ConnectionError as e:
            print(f"Redis not ready (attempt {attempt + 1}/{retries}): {e}")
            time.sleep(delay)
    raise RuntimeError("Could not connect to Redis after multiple retries")


# Module-level client, initialized to None — set during app startup
r = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global r
    r = connect_redis()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    r.ping()
    return {"status": "ok"}


@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    r.lpush("job", job_id)
    r.hset(f"job:{job_id}", mapping={"status": "queued"})
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        return {"error": "not found"}
    return {"job_id": job_id, "status": status.decode()}
