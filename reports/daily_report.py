import redis
import json
from collections import defaultdict
from datetime import date

# Redis connection
REDIS_HOST = "redis"
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def generate_daily_report():
    # Read processed events (not the queue)
    events = r.lrange("processed_events", 0, -1)

    prices = defaultdict(list)

    for event in events:
        data = json.loads(event)
        prices[data["symbol"]].append(float(data["price"]))

    report = {}

    for symbol, values in prices.items():
        report[symbol] = {
            "date": str(date.today()),
            "count": len(values),
            "average": round(sum(values) / len(values), 2),
            "max": max(values),
            "min": min(values)
        }

    # Save report as JSON file
    file_name = f"/app/reports/report_{date.today()}.json"
    with open(file_name, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Daily report generated: {file_name}")

if __name__ == "__main__":
    generate_daily_report()

