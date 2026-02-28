from fastapi import FastAPI
import redis, json, os

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

@app.post("/ingest")
def ingest(event: dict):
    r.lpush("events", json.dumps(event))
    return {"status": "queued", "event": event}

