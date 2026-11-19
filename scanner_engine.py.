
import requests
from datetime import datetime, timezone

BINANCE_URL = "https://api.binance.com/api/v3/klines"

COINS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT",
    "SOLUSDT", "XRPUSDT", "DOGEUSDT",
    "ADAUSDT", "LINKUSDT", "AVAXUSDT",
    "LTCUSDT", "DOTUSDT", "TRXUSDT",
    "NEARUSDT", "SUIUSDT", "APTUSDT",
    "UNIUSDT", "ATOMUSDT", "ETCUSDT",
    "FILUSDT", "AAVEUSDT", "HYPEUSDT",
    "PUMPUSDT"
]


def calculate_ema(values, period):
    alpha = 2 / (period + 1)
    result = values[0]

    for value in values[1:]:
        result = (
            alpha * value
            + (1 - alpha) * result
        )

    return result


def calculate_rsi(values, period=14):
    changes = [
        values[i] - values[i - 1]
        for i in range(1, len(values))
    ]

    recent = changes[-period:]

    gains = [max(x, 0) for x in recent]
    losses = [max(-x, 0) for x in recent]

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        return 100 if avg_gain > 0 else 50

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def analyze_coin(symbol):
    response = requests.get(
        BINANCE_URL,
        params={
            "symbol": symbol,
            "interval": "1h",
            "limit": 100
        },
        timeout=15
    )

    response.raise_for_status()

    # Abaikan candle yang masih berjalan
    candles = response.json()[:-1]

    if len(candles) < 60:
        raise ValueError("Data candle tidak cukup")

    close = [float(x[4]) for x in candles]
    high = [float(x[2]) for x in candles]
    volume = [float(x[5]) for x in candles]

    price = close[-1]

    ema20 = calculate_ema(close[-20:], 20)
    ema50 = calculate_ema(close[-50:], 50)
    rsi = calculate_rsi(close)

    avg_volume = sum(volume[-21:-1]) / 20

    volume_ratio = (
        volume[-1] / avg_volume
        if avg_volume > 0 else 0
    )

    previous_high = max(high[-21:-1])

    breakout = price > previous_high

    score = 0

    if ema20 > ema50:
        score += 30

    if price > ema20:
        score += 20

    if 50 <= rsi <= 65:
        score += 20

    if volume_ratio >= 1.5:
        score += 20

    if breakout:
        score += 10

    # ATR sederhana: rata-rata rentang high-low
    ranges = [
        float(x[2]) - float(x[3])
        for x in candles[-14:]
    ]

    atr = sum(ranges) / len(ranges)

    return {
        "coin": symbol,
        "price": price,
        "ema20": ema20,
        "ema50": ema50,
        "rsi": rsi,
        "volume": volume_ratio,
        "score": score,
        "breakout": breakout,
        "entry": price,
        "sl": price - 1.5 * atr,
        "tp1": price + atr,
        "tp2": price + 2 * atr,
        "tp3": price + 3 * atr,
        "time": datetime.now(
            timezone.utc
        ).strftime("%Y-%m-%d %H:%M UTC")
    }


def scan_market(coins=None):
    symbols = coins or COINS
    results = []
    errors = []

    for symbol in symbols:
        try:
            result = analyze_coin(symbol)
            results.append(result)

        except Exception as error:
            errors.append({
                "coin": symbol,
                "error": str(error)
            })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return {
        "results": results,
        "top5": results[:5],
        "errors": errors
    }
