
import requests
import time
from datetime import datetime

COINS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT",
    "BNBUSDT", "XRPUSDT", "DOGEUSDT",
    "ADAUSDT", "LINKUSDT", "AVAXUSDT",
    "LTCUSDT"
]

URL = "https://api.binance.com/api/v3/klines"
INTERVAL = "1h"
last_alerted = {}

# Isi token dan chat ID di config.py
from config import TOKEN, CHAT_ID


def telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        r = requests.post(
            url,
            data={"chat_id": CHAT_ID, "text": message},
            timeout=15
        )
        r.raise_for_status()
        return r.json().get("ok", False)
    except Exception as e:
        print("Telegram error:", e)
        return False


def ema(values, period):
    result = values[0]
    multiplier = 2 / (period + 1)

    for price in values[1:]:
        result = (price * multiplier) + (
            result * (1 - multiplier)
        )

    return result


def calculate_rsi(values, period=14):
    gains = []
    losses = []

    for i in range(1, len(values)):
        change = values[i] - values[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100 if avg_gain > 0 else 50

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def scan_coin(symbol):
    response = requests.get(
        URL,
        params={
            "symbol": symbol,
            "interval": INTERVAL,
            "limit": 100
        },
        timeout=15
    )
    response.raise_for_status()

    data = response.json()

    # Abaikan candle terakhir yang masih berjalan
    candles = data[:-1]
    prices = [float(c[4]) for c in candles]

    if len(prices) < 50:
        return

    price = prices[-1]
    ema20 = ema(prices[-20:], 20)
    ema50 = ema(prices[-50:], 50)
    rsi = calculate_rsi(prices)

    candle_time = candles[-1][0]

    print(
        f"{symbol} | Harga: {price} | "
        f"EMA20: {ema20:.6f} | "
        f"EMA50: {ema50:.6f} | RSI: {rsi:.2f}"
    )

    if (
        ema20 > ema50
        and price > ema20
        and 50 <= rsi <= 65
    ):
        if last_alerted.get(symbol) == candle_time:
            return

        message = (
            "POTENTIAL BULLISH SIGNAL\n\n"
            f"Coin: {symbol}\n"
            f"Harga: {price}\n"
            f"EMA20: {ema20:.6f}\n"
            f"EMA50: {ema50:.6f}\n"
            f"RSI: {rsi:.2f}\n"
            "Timeframe: 1H\n"
            "Status: BUY CANDIDATE\n"
            "Periksa chart sebelum entry."
        )

        if telegram(message):
            last_alerted[symbol] = candle_time
            print("Telegram alert berhasil dikirim!")


print("=== MULTI COIN SCANNER ===")
print("Jumlah koin:", len(COINS))

while True:
    print("\nWaktu scan:", datetime.now())

    for coin in COINS:
        try:
            scan_coin(coin)
        except Exception as e:
            print("Error", coin, ":", e)

    print("\nScan selesai. Menunggu 5 menit.")
    time.sleep(300)

