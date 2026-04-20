from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import redis, json, os

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

@app.post("/ingest")
def ingest(event: dict):
    r.lpush("processed_events", json.dumps(event))
    return {"status": "queued", "event": event}

# 👇 MUST HAVE
app.mount("/reports", StaticFiles(directory="/app/reports"), name="reports")
