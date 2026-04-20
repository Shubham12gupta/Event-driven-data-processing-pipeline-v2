import redis, json
from collections import defaultdict
from datetime import date, datetime
import pytz
from fpdf import FPDF

r = redis.Redis(host="redis", port=6379, decode_responses=True)

def is_market_day():
    est = pytz.timezone("US/Eastern")
    now = datetime.now(est)
    return now.weekday() < 5

if not is_market_day():
    print(f"Today ({date.today()}) is not a trading day. Skipping report.")
    exit(0)

today_str = str(date.today())

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
    print(f"No valid data found for today ({today_str}). Skipping report.")
    exit(0)


class StockPDF(FPDF):

    def header(self):
        # Dark navy top bar
        self.set_fill_color(15, 32, 65)
        self.rect(0, 0, 210, 28, 'F')

        # White title
        self.set_y(7)
        self.set_font("Arial", "B", 18)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "Daily Stock Market Report", ln=False, align="C")

        # Gold underline accent
        self.set_draw_color(255, 193, 7)
        self.set_line_width(0.8)
        self.line(10, 20, 200, 20)

        self.ln(20)

    def footer(self):
        self.set_y(-15)
        # Footer bar
        self.set_fill_color(15, 32, 65)
        self.rect(0, 282, 210, 15, 'F')
        self.set_font("Arial", "I", 8)
        self.set_text_color(180, 180, 180)
        self.cell(0, 10, f"Generated on {today_str}  |  Page {self.page_no()}  |  Confidential", align="C")

    def date_banner(self, today_str):
        self.set_fill_color(240, 244, 255)
        self.set_draw_color(200, 210, 240)
        self.set_line_width(0.3)
        self.rect(10, self.get_y(), 190, 10, 'FD')
        self.set_font("Arial", "", 10)
        self.set_text_color(60, 60, 100)
        self.cell(0, 10, f"Report Date:  {today_str}    |    Market: NYSE / NASDAQ", align="C", ln=True)
        self.ln(4)

    def stock_header(self, symbol):
        # Teal section header
        self.set_fill_color(0, 123, 167)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 13)
        self.cell(0, 11, f"  Stock: {symbol}", ln=True, fill=True)
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
        self.cell(120, 8, str(value), border="B", fill=True, ln=True)

    def trend_row(self, trend):
        is_up = trend == "UP"
        self.set_font("Arial", "B", 10)
        self.set_fill_color(245, 250, 255)
        self.set_text_color(50, 50, 50)
        self.cell(70, 8, "  Trend", border="B", fill=True)

        # Green for UP, Red for DOWN
        if is_up:
            self.set_fill_color(220, 255, 220)
            self.set_text_color(0, 140, 0)
        else:
            self.set_fill_color(255, 220, 220)
            self.set_text_color(180, 0, 0)

        self.set_font("Arial", "B", 10)
        arrow = "▲ UP" if is_up else "▼ DOWN"
        self.cell(120, 8, f"  {arrow}", border="B", fill=True, ln=True)

    def table_header(self):
        self.ln(3)
        self.set_fill_color(30, 60, 114)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 10)
        self.cell(100, 9, "  Timestamp", border=0, fill=True)
        self.cell(85,  9, "  Price (USD)", border=0, fill=True, ln=True)

    def table_row(self, time_val, price_val, row_index):
        # Alternating row colors
        if row_index % 2 == 0:
            self.set_fill_color(245, 248, 255)
        else:
            self.set_fill_color(255, 255, 255)

        self.set_text_color(40, 40, 40)
        self.set_font("Arial", "", 10)
        self.cell(100, 8, f"  {time_val}", border=0, fill=True)

        # Price in dark teal
        self.set_text_color(0, 100, 130)
        self.set_font("Arial", "B", 10)
        self.cell(85, 8, f"  $ {price_val}", border=0, fill=True, ln=True)

    def divider(self):
        self.set_draw_color(200, 210, 240)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)


# ─── Build PDF ────────────────────────────────────────────────────────────────

pdf = StockPDF()
pdf.set_auto_page_break(auto=True, margin=18)
pdf.add_page()

pdf.date_banner(today_str)

for symbol, values in prices.items():
    avg   = round(sum(values) / len(values), 2)
    high  = max(values)
    low   = min(values)
    trend = "UP" if values[-1] > values[0] else "DOWN"

    pdf.stock_header(symbol)

    pdf.stat_row("Total Records",  len(values),       highlight=False)
    pdf.stat_row("Average Price",  f"$ {avg:.2f}",    highlight=True)
    pdf.stat_row("Highest Price",  f"$ {high:.2f}",   highlight=False)
    pdf.stat_row("Lowest Price",   f"$ {low:.2f}",    highlight=True)
    pdf.trend_row(trend)

    pdf.table_header()

    today_records = records[symbol][-10:]  # last 10 records
    for i, rec in enumerate(today_records):
        pdf.table_row(rec["time"], rec["price"], i)

    pdf.divider()

filename = f"/app/reports/Daily_Report_{today_str}.pdf"
pdf.output(filename)
print(f"PDF report generated: {filename}")
