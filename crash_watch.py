import yfinance as yf
import requests
import pandas as pd

# --- CONFIG ---

WATCHLIST = [
    "NVDA", "TSLA", "META", "AMZN", "PLTR",
    "QQQ", "ARKK", "SBUX", "NKE", "BKNG",
    "CVNA", "FRC", "PACW", "XLF", "VNQ",
    "IYR", "IWM"
]

PRICE_DROP_THRESHOLD = 0.05  # 5% drop triggers alert
VOLUME_SPIKE_MULTIPLIER = 2  # volume > 2x avg volume triggers alert

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

def check_stock(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="10d")
        if hist.empty or len(hist) < 5:
            print(f"Not enough data for {symbol}")
            return None

        # Calculate price drop since yesterday
        today_close = hist['Close'].iloc[-1]
        yesterday_close = hist['Close'].iloc[-2]
        price_drop_pct = (yesterday_close - today_close) / yesterday_close

        # Average volume over last 5 days
        avg_volume = hist['Volume'][-6:-1].mean()
        today_volume = hist['Volume'].iloc[-1]

        volume_spike = today_volume > avg_volume * VOLUME_SPIKE_MULTIPLIER

        alert_msgs = []
        if price_drop_pct >= PRICE_DROP_THRESHOLD:
            alert_msgs.append(f"{symbol} price dropped {price_drop_pct*100:.2f}% today.")
        if volume_spike:
            alert_msgs.append(f"{symbol} volume spiked to {today_volume:,}, avg {avg_volume:,.0f}.")

        if alert_msgs:
            message = "\n".join(alert_msgs)
            send_telegram_message(message)
            print(f"Alert sent for {symbol}: {message}")
        else:
            print(f"No alert for {symbol}")
    except Exception as e:
        print(f"Error checking {symbol}: {e}")

def main():
    for symbol in WATCHLIST:
        check_stock(symbol)

if __name__ == "__main__":
    main()
