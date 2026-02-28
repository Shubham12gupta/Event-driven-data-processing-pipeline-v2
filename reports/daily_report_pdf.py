import redis, json
from collections import defaultdict
from datetime import date
from fpdf import FPDF

r = redis.Redis(host="redis", port=6379, decode_responses=True)

events = r.lrange("processed_events", 0, -1)
prices = defaultdict(list)

for event in events:
    data = json.loads(event)
    prices[data["symbol"]].append(float(data["price"]))

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

pdf.cell(200, 10, txt="Daily Stock Market Summary Report", ln=True)
pdf.cell(200, 10, txt=f"Date: {date.today()}", ln=True)
pdf.ln(5)

for symbol, values in prices.items():
    avg = sum(values) / len(values)
    pdf.multi_cell(0, 8,
        f"Stock: {symbol}\n"
        f"Total Records: {len(values)}\n"
        f"Average Price: {avg:.2f}\n"
        f"Highest Price: {max(values)}\n"
        f"Lowest Price: {min(values)}\n"
    )
    pdf.ln(3)

pdf.output(f"/app/reports/Daily_Report_{date.today()}.pdf")

print("PDF report generated")

