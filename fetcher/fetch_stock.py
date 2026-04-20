import requests
import time
import os
from datetime import datetime
import pytz

API_KEY = os.getenv("FINNHUB_API_KEY")

if not API_KEY:
    raise ValueError("❌ FINNHUB_API_KEY not set")

URL = "https://finnhub.io/api/v1/quote"

def is_market_open():
    """NYSE market hours: Mon-Fri 9:30am - 4:00pm EST"""
    est = pytz.timezone("US/Eastern")
    now = datetime.now(est)

    # Reject Saturday (5) and Sunday (6)
    if now.weekday() >= 5:
        return False

    market_open  = now.replace(hour=9,  minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0,  second=0, microsecond=0)

    return market_open <= now <= market_close

while True:
    try:
        if not is_market_open():
            print(f"⏸ Market closed. Sleeping 5 minutes...")
            time.sleep(300)
            continue

        response = requests.get(
            URL,
            params={
                "symbol": "AAPL",
                "token": API_KEY
            }
        ).json()

        if "c" not in response:
            print("❌ API error:", response)
            time.sleep(60)
            continue

        price = response["c"]

        # Reject zero or invalid prices (Finnhub returns 0 when market closed)
        if price <= 0:
            print(f"⚠️ Invalid price received: {price}. Skipping.")
            time.sleep(60)
            continue

        data = {
            "symbol": "AAPL",
            "price": price,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        print("✅ Sending:", data)
        requests.post("http://api:8000/ingest", json=data)

    except Exception as e:
        print("❌ Error:", e)

    time.sleep(60)
