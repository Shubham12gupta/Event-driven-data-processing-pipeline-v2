import redis, json
from collections import defaultdict
from datetime import date, datetime
import pytz
from fpdf import FPDF
import os

r = redis.Redis(host="redis", port=6379, decode_responses=True)

ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(ist)
today_str = str(date.today())
snapshot_time = now_ist.strftime("%H:%M:%S")

# Read today's data from Redis
events  = r.lrange("processed_events", 0, -1)
prices  = defaultdict(list)
records = defaultdict(list)

for event in events:
    data = json.loads(event)
    if not data["time"].startswith(today_str):
        continue
    price = float(data["price"])
    if price <= 0:
        continue
    symbol = data["symbol"]
    prices[symbol].append(price)
    records[symbol].append(data)

if not prices:
    print(f"No valid data for today ({today_str}). Skipping snapshot.")
    exit(0)


class CryptoPDF(FPDF):

    def header(self):
        # Dark navy top bar
        self.set_fill_color(15, 32, 65)
        self.rect(0, 0, 210, 28, 'F')
        self.set_y(7)
        self.set_font("Arial", "B", 18)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "Crypto Market Report", ln=False, align="C")
        # Gold underline
        self.set_draw_color(255, 193, 7)
        self.set_line_width(0.8)
        self.line(10, 20, 200, 20)
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_fill_color(15, 32, 65)
        self.rect(0, 282, 210, 15, 'F')
        self.set_font("Arial", "I", 8)
        self.set_text_color(180, 180, 180)
        self.cell(0, 10,
            f"Generated on {today_str}  |  Page {self.page_no()}  |  Data: CoinGecko API",
            align="C")

    def date_banner(self):
        self.set_fill_color(240, 244, 255)
        self.set_draw_color(200, 210, 240)
        self.set_line_width(0.3)
        self.rect(10, self.get_y(), 190, 10, 'FD')
        self.set_font("Arial", "", 10)
        self.set_text_color(60, 60, 100)
        self.cell(0, 10,
            f"Report Date: {today_str}  |  Source: CoinGecko  |  Currency: INR",
            align="C", ln=True)
        self.ln(4)

    def snapshot_banner(self, snapshot_time, snapshot_num):
        # Gold snapshot banner
        self.set_fill_color(255, 193, 7)
        self.set_text_color(15, 32, 65)
        self.set_font("Arial", "B", 11)
        self.cell(0, 9,
            f"  SNAPSHOT #{snapshot_num}   |   Captured At: {snapshot_time} IST   |   Date: {today_str}",
            ln=True, fill=True)
        self.ln(3)

    def coin_header(self, symbol):
        self.set_fill_color(0, 123, 167)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"  {symbol}", ln=True, fill=True)
        self.ln(2)

    def stat_row(self, label, value, highlight=False):
        if highlight:
            self.set_fill_color(245, 250, 255)
        else:
            self.set_fill_color(255, 255, 255)
        self.set_text_color(50, 50, 50)
        self.set_font("Arial", "B", 10)
        self.cell(70, 8, f"  {label}", border="B", fill=True)
        self.set_font("Arial", "", 10)
        self.set_text_color(30, 30, 30)
        self.cell(120, 8, str(value), border="B", fill=True, ln=True)

    def trend_row(self, trend):
        is_up = trend == "UP"
        self.set_font("Arial", "B", 10)
        self.set_fill_color(245, 250, 255)
        self.set_text_color(50, 50, 50)
        self.cell(70, 8, "  Trend", border="B", fill=True)
        if is_up:
            self.set_fill_color(220, 255, 220)
            self.set_text_color(0, 140, 0)
        else:
            self.set_fill_color(255, 220, 220)
            self.set_text_color(180, 0, 0)
        self.set_font("Arial", "B", 10)
        arrow = "  >> UP" if is_up else "  >> DOWN"
        self.cell(120, 8, arrow, border="B", fill=True, ln=True)

    def change_row(self, change_24h):
        is_pos = change_24h >= 0
        self.set_font("Arial", "B", 10)
        self.set_fill_color(245, 250, 255)
        self.set_text_color(50, 50, 50)
        self.cell(70, 8, "  24h Change", border="B", fill=True)
        if is_pos:
            self.set_fill_color(220, 255, 220)
            self.set_text_color(0, 140, 0)
        else:
            self.set_fill_color(255, 220, 220)
            self.set_text_color(180, 0, 0)
        self.set_font("Arial", "B", 10)
        sign = "+" if is_pos else ""
        self.cell(120, 8, f"  {sign}{change_24h:.2f}%", border="B", fill=True, ln=True)

    def table_header(self):
        self.ln(3)
        self.set_fill_color(30, 60, 114)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 10)
        self.cell(90, 9, "  Timestamp", border=0, fill=True)
        self.cell(55, 9, "  Price (INR)", border=0, fill=True)
        self.cell(45, 9, "  Price (USD)", border=0, fill=True, ln=True)

    def table_row(self, rec, row_index):
        if row_index % 2 == 0:
            self.set_fill_color(245, 248, 255)
        else:
            self.set_fill_color(255, 255, 255)
        self.set_text_color(40, 40, 40)
        self.set_font("Arial", "", 10)
        self.cell(90, 8, f"  {rec['time']}", border=0, fill=True)
        self.set_text_color(0, 100, 130)
        self.set_font("Arial", "B", 10)
        self.cell(55, 8, f"  Rs.{rec['price']}", border=0, fill=True)
        self.set_text_color(80, 80, 80)
        self.set_font("Arial", "", 10)
        usd = rec.get("price_usd", "-")
        self.cell(45, 8, f"  ${usd}", border=0, fill=True, ln=True)

    def divider(self):
        self.set_draw_color(200, 210, 240)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def summary_box(self, total_coins, total_records):
        self.set_fill_color(15, 32, 65)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 10)
        self.cell(95, 9, f"  Total Coins Tracked: {total_coins}", fill=True)
        self.cell(95, 9, f"  Total Data Points: {total_records}", fill=True, ln=True)
        self.ln(4)


# ── Snapshot number tracker ────────────────────────────────────────────────
filename     = f"/app/reports/Daily_Report_{today_str}.pdf"
tracker_file = f"/app/reports/.snapshot_count_{today_str}.txt"

if os.path.exists(tracker_file):
    with open(tracker_file, "r") as f:
        snapshot_num = int(f.read().strip()) + 1
else:
    snapshot_num = 1

with open(tracker_file, "w") as f:
    f.write(str(snapshot_num))


# ── Build PDF ──────────────────────────────────────────────────────────────
pdf = CryptoPDF()
pdf.set_auto_page_break(auto=True, margin=18)
pdf.add_page()

# Date banner + summary
pdf.date_banner()
total_records = sum(len(v) for v in prices.values())
pdf.summary_box(len(prices), total_records)

# Current snapshot
pdf.snapshot_banner(snapshot_time, snapshot_num)

for symbol, values in prices.items():
    avg    = round(sum(values) / len(values), 2)
    high   = max(values)
    low    = min(values)
    trend  = "UP" if values[-1] > values[0] else "DOWN"

    # 24h change from latest record
    latest_rec  = records[symbol][-1]
    change_24h  = float(latest_rec.get("change_24h", 0))

    pdf.coin_header(symbol)
    pdf.stat_row("Total Records",  len(values),         highlight=False)
    pdf.stat_row("Average Price",  f"Rs. {avg:,.2f}",   highlight=True)
    pdf.stat_row("Highest Price",  f"Rs. {high:,.2f}",  highlight=False)
    pdf.stat_row("Lowest Price",   f"Rs. {low:,.2f}",   highlight=True)
    pdf.trend_row(trend)
    pdf.change_row(change_24h)
    pdf.table_header()

    for i, rec in enumerate(records[symbol][-5:]):
        pdf.table_row(rec, i)

    pdf.divider()


# ── Previous snapshots from Redis ─────────────────────────────────────────
prev_snapshots = r.lrange(f"snapshots:{today_str}", 0, -1)

for snap_raw in prev_snapshots:
    snap = json.loads(snap_raw)
    pdf.add_page()
    pdf.snapshot_banner(snap["time"], snap["num"])

    for symbol, sdata in snap["data"].items():
        pdf.coin_header(symbol)
        pdf.stat_row("Total Records", sdata["count"],                    highlight=False)
        pdf.stat_row("Average Price", f"Rs. {sdata['avg']:,.2f}",        highlight=True)
        pdf.stat_row("Highest Price", f"Rs. {sdata['high']:,.2f}",       highlight=False)
        pdf.stat_row("Lowest Price",  f"Rs. {sdata['low']:,.2f}",        highlight=True)
        pdf.trend_row(sdata["trend"])
        pdf.change_row(float(sdata.get("change_24h", 0)))
        pdf.table_header()
        for i, rec in enumerate(sdata["records"]):
            pdf.table_row(rec, i)
        pdf.divider()


# ── Save current snapshot to Redis ────────────────────────────────────────
snap_data = {}
for symbol, values in prices.items():
    latest_rec = records[symbol][-1]
    snap_data[symbol] = {
        "count":      len(values),
        "avg":        round(sum(values) / len(values), 2),
        "high":       max(values),
        "low":        min(values),
        "trend":      "UP" if values[-1] > values[0] else "DOWN",
        "change_24h": float(latest_rec.get("change_24h", 0)),
        "records":    records[symbol][-5:]
    }

r.rpush(f"snapshots:{today_str}", json.dumps({
    "time": snapshot_time,
    "num":  snapshot_num,
    "data": snap_data
}))

# ── Output ─────────────────────────────────────────────────────────────────
pdf.output(filename)
print(f"Snapshot #{snapshot_num} added -> {filename}")
