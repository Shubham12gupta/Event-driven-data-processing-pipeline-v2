import redis, json, time, os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

print("Worker started")

while True:
    event = r.brpop("events", timeout=5)
    if event:
        data = json.loads(event[1])

        # store processed data for reporting
        r.lpush("processed_events", json.dumps(data))

        print("Processed:", data)

    time.sleep(1)

