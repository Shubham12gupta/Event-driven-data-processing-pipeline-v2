import requests
import time
from datetime import datetime
import pytz

COINS = ["bitcoin", "ethereum", "dogecoin"]  # add/remove jitne chahiye

def get_crypto_prices():
    response = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={
            "ids":           ",".join(COINS),
            "vs_currencies": "inr,usd",
            "include_24hr_change": "true"
        },
        timeout=10
    ).json()
    return response

while True:
    try:
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)

        prices = get_crypto_prices()

        for coin, data in prices.items():
            price_inr = data.get("inr", 0)
            price_usd = data.get("usd", 0)
            change_24h = data.get("inr_24h_change", 0)

            if price_inr <= 0:
                print(f"Invalid price for {coin}. Skipping.")
                continue

            payload = {
                "symbol":     coin.upper(),
                "price":      round(price_inr, 2),
                "price_usd":  round(price_usd, 2),
                "change_24h": round(change_24h, 2),
                "time":       now.strftime("%Y-%m-%d %H:%M:%S")
            }

            print(f"Sending: {payload}")
            requests.post("http://api:8000/ingest", json=payload, timeout=5)

    except Exception as e:
        print("Error:", e)

    time.sleep(60)  # har 60 second mein fetch
