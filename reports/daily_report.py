import redis, json
from collections import defaultdict
from datetime import date, datetime
import pytz

REDIS_HOST = "redis"
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def is_market_day():
    est = pytz.timezone("US/Eastern")
    now = datetime.now(est)
    return now.weekday() < 5

def generate_daily_report():
    if not is_market_day():
        print(f"⏸ Today ({date.today()}) is not a trading day. Skipping.")
        return

    today_str = str(date.today())
    events    = r.lrange("processed_events", 0, -1)
    prices    = defaultdict(list)

    for event in events:
        data = json.loads(event)

        # Only today's data
        if not data["time"].startswith(today_str):
            continue

        price = float(data["price"])

        # Reject invalid prices
        if price <= 0:
            continue

        prices[data["symbol"]].append(price)

    if not prices:
        print(f"⚠️ No valid data for today ({today_str}). Skipping report.")
        return

    report = {}
    for symbol, values in prices.items():
        report[symbol] = {
            "date":    today_str,
            "count":   len(values),
            "average": round(sum(values) / len(values), 2),
            "max":     max(values),
            "min":     min(values)
        }

    file_name = f"/app/reports/report_{today_str}.json"
    with open(file_name, "w") as f:
        json.dump(report, f, indent=2)

    print(f"✅ Daily report generated: {file_name}")

if __name__ == "__main__":
    generate_daily_report()
