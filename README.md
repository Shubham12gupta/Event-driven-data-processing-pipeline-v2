<img width="979" height="831" alt="image" src="https://github.com/user-attachments/assets/1595870e-6780-455a-9b18-d504951bdd8d" />

📊 Event-Driven Stock Market Data Processing Pipeline
📌 Overview

This project implements an event-driven, containerized data processing pipeline that ingests stock market data, processes it asynchronously, and generates automated PDF reports at fixed intervals.

The system is designed to mimic real-world production behavior, including market-hour awareness, asynchronous processing, and fully automated reporting and deployment.

🧠 Key Features

🚀 FastAPI for data ingestion

🔁 Redis as an event queue

⚙️ Worker service for asynchronous processing

📄 Automated PDF report generation every 6 hours

🌐 Reports accessible via browser (no manual download)

🐳 Docker Compose based multi-service architecture

🔄 CI/CD pipeline using GitHub Actions

📆 Market-aware logic (weekends handled gracefully)

🏗️ Architecture
Stock Data Source / Fetcher
          |
          v
     FastAPI (/ingest)
          |
          v
        Redis
     (events queue)
          |
          v
        Worker
          |
          v
   Redis (processed_events)
          |
          v
 Automated PDF Report Generator
          |
          v
 Browser Access (/reports)

🧩 Services
🔹 API Service

Accepts incoming stock events via /ingest

Pushes events into Redis queue

Serves generated PDF reports via /reports

🔹 Worker Service

Consumes events from Redis

Stores processed data for reporting

Automatically generates PDF reports every 6 hours

🔹 Fetcher Service

Fetches or simulates stock market data

Sends data to API for ingestion

🔹 Redis

Acts as a message broker and temporary datastore

⏱️ Automation Logic

Reports are generated every 6 hours using a container-native scheduler loop

No system cron or manual execution required

On weekends (market closed), reports indicate “Market Closed”

On weekdays, reports include stock summaries if data is available

📄 Sample Report Output
Daily Stock Market Summary Report
Date: 2026-02-07

Market Status: Closed (Weekend)
No trading data available.


Or on trading days:

Stock: AAPL
Total Records: 12
Average Price: 182.40
Highest Price: 185.10
Lowest Price: 180.75

🌐 Accessing Reports

Once generated, reports are automatically available via browser:

http://<VM_IP>:8000/reports/


Or directly:

http://<VM_IP>:8000/reports/Daily_Report_YYYY-MM-DD.pdf

🐳 Running the Project
Prerequisites

Docker

Docker Compose

Start the system
docker-compose up -d --build

Stop the system
docker-compose down

🔄 CI/CD Pipeline
Continuous Integration (CI)

Triggered on every push to main

Builds Docker images

Starts containers

Performs API health check

Continuous Deployment (CD)

On successful push, deploys latest code to VM

Restarts Docker services automatically

🧪 Test Ingestion (Optional)

To manually test data flow:

curl -X POST http://<VM_IP>:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","price":182.4,"time":"2026-02-07 12:00"}'

🧠 Design Decisions

Event-driven architecture ensures loose coupling

Redis queues enable fault-tolerant async processing

Dockerized services provide portability and consistency

Automated reporting eliminates manual intervention

Market-aware logic avoids generating misleading data

📌 Conclusion

This project demonstrates a realistic, production-style data pipeline with automation, scalability, and robustness.
It showcases best practices in distributed systems, containerization, and CI/CD workflows.

👨‍💻 Author

Shubham Gupta
Event-Driven Systems | Docker | FastAPI | Redis | CI/CD
