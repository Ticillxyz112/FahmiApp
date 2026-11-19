import requests
import time

from config import TOKEN, CHAT_ID

COINS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT",
    "SOLUSDT", "XRPUSDT", "DOGEUSDT",
    "ADAUSDT", "LINKUSDT", "AVAXUSDT",
    "LTCUSDT", "DOTUSDT", "TRXUSDT",
    "NEARUSDT", "SUIUSDT", "APTUSDT",
    "UNIUSDT", "ATOMUSDT", "ETCUSDT",
    "FILUSDT", "AAVEUSDT", "PUMPUSDT","HYPEUSDT"
]

URL = "https://api.binance.com/api/v3/klines"


def get_data(symbol):
    r = requests.get(
        URL,
        params={
            "symbol": symbol,
            "interval": "1h",
            "limit": 60
        },
        timeout=15
    )
    r.raise_for_status()

    # Abaikan candle yang masih berjalan
    data = r.json()[:-1]

    close = [float(x[4]) for x in data]
    volume = [float(x[5]) for x in data]

    return close, volume, data


def ema(values, period):
    result = values[0]
    alpha = 2 / (period + 1)

    for value in values[1:]:
        result = alpha * value + (1-alpha) * result

    return result


def rsi(values):
    changes = [
        values[i] - values[i-1]
        for i in range(1, len(values))
    ]

    gains = [max(x, 0) for x in changes[-14:]]
    losses = [max(-x, 0) for x in changes[-14:]]

    avg_gain = sum(gains) / 14
    avg_loss = sum(losses) / 14

    if avg_loss == 0:
        return 100 if avg_gain > 0 else 50

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def analyze(symbol):
    close, volume, data = get_data(symbol)

    price = close[-1]
    ema20 = ema(close[-20:], 20)
    ema50 = ema(close[-50:], 50)
    momentum = rsi(close)

    avg_volume = sum(volume[-21:-1]) / 20
    volume_ratio = volume[-1] / avg_volume if avg_volume else 0

    previous_high = max(
        float(x[2]) for x in data[-21:-1]
    )

    score = 0

    if ema20 > ema50:
        score += 30

    if price > ema20:
        score += 20

    if 50 <= momentum <= 65:
        score += 20

    if volume_ratio >= 1.5:
        score += 20

    if price > previous_high:
        score += 10

    atr_range = sum(
        float(x[2]) - float(x[3])
        for x in data[-15:]
    ) / 14

    # ATR sederhana untuk estimasi risiko
    sl = price - (1.5 * atr_range)
    tp1 = price + atr_range
    tp2 = price + (2 * atr_range)
    tp3 = price + (3 * atr_range)

    return {
        "coin": symbol,
        "price": price,
        "rsi": momentum,
        "volume": volume_ratio,
        "score": score,
        "breakout": price > previous_high,
        "entry": price,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3
    }


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    r = requests.post(
        url,
        data={"chat_id": CHAT_ID, "text": message},
        timeout=15
    )
    r.raise_for_status()

    if not r.json().get("ok"):
        print("Telegram gagal:", r.text)


while True:
    print("\n=== SMART SCANNER ===")

    results = []

    for coin in COINS:
        try:
            result = analyze(coin)
            results.append(result)

            print(
                coin,
                "| Score:", result["score"],
                "| RSI:", round(result["rsi"], 2),
                "| Volume:", round(result["volume"], 2)
            )

        except Exception as e:
            print("Error", coin, ":", e)

        time.sleep(0.2)

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    top5 = results[:5]

    message = "SMART SCANNER - TOP 5 COINS\n\n"

    for i, x in enumerate(top5, 1):
        message += (
            f"{i}. {x['coin']}\n"
            f"Score: {x['score']}/100\n"
            f"Price: {x['price']}\n"
            f"RSI: {x['rsi']:.2f}\n"
            f"Volume: {x['volume']:.2f}x\n"
            f"Breakout: {x['breakout']}\n"
            f"Entry: {x['entry']:.6f}\n"
            f"SL: {x['sl']:.6f}\n"
            f"TP1: {x['tp1']:.6f}\n"
            f"TP2: {x['tp2']:.6f}\n"
            f"TP3: {x['tp3']:.6f}\n\n"
        )

    message += "Sinyal ini untuk pemantauan, bukan perintah BUY."

    print("\nTOP 5:")
    for x in top5:
        print(x["coin"], x["score"])

    if results:
        try:
            send_telegram(message)
            print("Laporan Telegram terkirim.")
        except Exception as e:
            print("Telegram error:", e)

    print("\nMenunggu 5 menit...")
    time.sleep(300)

