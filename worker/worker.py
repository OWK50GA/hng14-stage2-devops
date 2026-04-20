import redis
import time
import os
import signal


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


r = connect_redis()

shutdown = False


def handle_shutdown(signum, frame):
    global shutdown
    print("Shutdown signal received, finishing current job...")
    shutdown = True


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)  # simulate work
    r.hset(f"job:{job_id}", mapping={"status": "completed"})
    print(f"Done: {job_id}")


while not shutdown:
    job = r.brpop("job", timeout=5)
    if job:
        _, job_id = job
        process_job(job_id.decode())

print("Worker exited cleanly.")
