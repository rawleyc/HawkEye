# HawkEye Crash Monitor Bot

## Overview

HawkEye is an automated stock crash monitoring system designed to track key U.S. stock tickers and ETFs for early warning signals of market downturns. It analyses daily price drops, volume spikes, technical indicators (like RSI and moving averages), and options market sentiment (put/call ratios) to send timely alerts via Telegram.

---

## What We Have So Far

- **Watchlist Monitoring:** Tracks ~15 tickers including tech stocks (NVDA, TSLA, META, AMZN), ETFs (QQQ, ARKK, XLF), and others.
- **Indicators:**  
  - Price drop thresholds (e.g., 5% daily drop)  
  - Volume spike detection (e.g., volume > 2x average)  
  - RSI oversold alerts (RSI < 30)  
  - Moving average break detection (50-day and 200-day)  
  - Put/Call ratio alerts (>1.5)
- **Data Sources:** Uses `yfinance` for historical stock data and scrapes Yahoo Finance for options data.
- **Alert Delivery:** Sends formatted alert messages via Telegram Bot API.
- **Automation:**  
  - GitHub webhook triggers automatic updates on server on code push.  
  - Virtual environment setup to manage dependencies cleanly.

---

## What’s Left To Do

- **CSV Export:**  
  - Save daily summary of alerts and monitored data to CSV files for historical analysis and backtesting.
- **Improved Error Handling:**  
  - Handle missing data and HTTP errors more gracefully, especially for put/call ratio scraping.
- **Options Data Source:**  
  - Explore more reliable or official APIs for options sentiment to replace fragile HTML scraping.
- **Deployment Hardening:**  
  - Add logging and alerting on the webhook listener side to monitor failures.  
  - Ensure security best practices for webhook endpoints (e.g., secret validation).
- **Extensibility:**  
  - Add more technical indicators (MACD, Bollinger Bands) or custom signals.  
  - Support configurable watchlists and alert thresholds via config files or environment variables.
- **User Interface:**  
  - Optional web dashboard to view current watchlist status, recent alerts, and historical data.

---

## How to Run

1. Clone the repo.
2. Setup and activate the Python virtual environment (`.venv`).
3. Install dependencies via `pip install -r requirements.txt`.
4. Set Telegram bot token and chat ID via environment variables or `.env` file.
5. Run `python crash_watch_v2.py` to start the monitoring script.
6. Configure GitHub webhook to auto-deploy updates on push.

---
