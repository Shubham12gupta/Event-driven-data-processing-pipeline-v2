import requests, time

API_KEY = 

URL = "https://www.alphavantage.co/query"

while True:
    response = requests.get(
        URL,
        params={
            "function": "TIME_SERIES_INTRADAY",
            "symbol": "AAPL",
            "interval": "5min",
            "apikey": API_KEY
        }
    ).json()

    latest = list(response["Time Series (5min)"].items())[0]

    data = {
        "symbol": "AAPL",
        "price": latest[1]["4. close"],
        "time": latest[0]
    }

    requests.post("http://api:8000/ingest", json=data)
    time.sleep(900)  # 15 min

