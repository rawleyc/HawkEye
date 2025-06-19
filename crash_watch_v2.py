import yfinance as yf
import requests
import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
import os
import urllib.request

# --- CONFIG ---

WATCHLIST = [
    "NVDA", "TSLA", "META", "AMZN", "PLTR",
    "QQQ", "ARKK", "SBUX", "NKE", "BKNG",
    "CVNA", "XLF", "VNQ", "IYR", "IWM"
]

PRICE_DROP_THRESHOLD = 0.05  # 5% drop triggers alert
VOLUME_SPIKE_MULTIPLIER = 2  # volume > 2x avg volume triggers alert
RSI_OVERSOLD = 30            # RSI below 30 is oversold
PUT_CALL_THRESHOLD = 1.5     # put/call ratio trigger

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# --- FUNCTIONS ---

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Exception during sending Telegram message: {e}")

def compute_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_put_call_ratio(symbol):
    try:
        url = f"https://finance.yahoo.com/quote/{symbol}/options?p={symbol}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all("script")
        text_blocks = [script.text for script in scripts if 'putCallRatio' in script.text]
        for block in text_blocks:
            match = re.search(r'\"putCallRatio\":([\d\.]+)', block)
            if match:
                return float(match.group(1))
    except Exception as e:
        print(f"Error retrieving put/call ratio for {symbol}: {e}")
    return None

def check_stock(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="60d")
        if hist.empty or len(hist) < 30:
            print(f"Not enough data for {symbol}")
            return

        today_close = hist['Close'].iloc[-1]
        yesterday_close = hist['Close'].iloc[-2]
        price_drop_pct = (yesterday_close - today_close) / yesterday_close

        avg_volume = hist['Volume'].iloc[-6:-1].mean()
        today_volume = hist['Volume'].iloc[-1]
        volume_spike = today_volume > avg_volume * VOLUME_SPIKE_MULTIPLIER

        ma50 = hist['Close'].rolling(50).mean().iloc[-1]
        ma200 = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None
        below_ma50 = today_close < ma50
        below_ma200 = ma200 and today_close < ma200

        rsi = compute_rsi(hist['Close']).iloc[-1]
        rsi_signal = rsi < RSI_OVERSOLD

        put_call_ratio = get_put_call_ratio(symbol)
        put_call_alert = put_call_ratio and put_call_ratio > PUT_CALL_THRESHOLD

        alert_msgs = []
        if price_drop_pct >= PRICE_DROP_THRESHOLD:
            alert_msgs.append(f"\u274c Price dropped {price_drop_pct*100:.2f}% today.")
        if volume_spike:
            alert_msgs.append(f"\u26a1 Volume spike: {today_volume:,} vs avg {avg_volume:,.0f}.")
        if below_ma50:
            alert_msgs.append("\ud83d\udcc9 Broke below 50-day MA.")
        if below_ma200:
            alert_msgs.append("\ud83d\udd25 Broke below 200-day MA.")
        if rsi_signal:
            alert_msgs.append(f"\u26a0 RSI is {rsi:.1f} (<30, oversold)")
        if put_call_alert:
            alert_msgs.append(f"\ud83d\udea8 Put/Call Ratio: {put_call_ratio:.2f} (> {PUT_CALL_THRESHOLD})")

        if alert_msgs:
            message = f"\ud83d\udd14 {symbol} Alert:\n" + "\n".join(alert_msgs)
            send_telegram_message(message)
            print(message)
        else:
            print(f"No alert for {symbol}")
    except Exception as e:
        print(f"Error checking {symbol}: {e}")

def main():
    for symbol in WATCHLIST:
        check_stock(symbol)

if __name__ == "__main__":
    main()

