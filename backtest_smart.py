
import requests
import time

COINS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT",
    "SOLUSDT", "XRPUSDT", "DOGEUSDT",
    "ADAUSDT", "LINKUSDT", "AVAXUSDT",
    "LTCUSDT", "HYPEUSDT", "PUMPUSDT"
]

URL = "https://api.binance.com/api/v3/klines"

STOP_LOSS = 0.02
TAKE_PROFIT = 0.04

# Asumsi biaya dan slippage per sisi
COST = 0.003


def get_candles(symbol):
    response = requests.get(
        URL,
        params={
            "symbol": symbol,
            "interval": "1h",
            "limit": 500
        },
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    # Abaikan candle terakhir yang belum selesai
    data = data[:-1]

    return {
        "open": [float(x[1]) for x in data],
        "high": [float(x[2]) for x in data],
        "low": [float(x[3]) for x in data],
        "close": [float(x[4]) for x in data],
        "volume": [float(x[5]) for x in data]
    }


def calculate_ema(values, period):
    result = [values[0]]
    alpha = 2 / (period + 1)

    for price in values[1:]:
        value = (
            price * alpha
            + result[-1] * (1 - alpha)
        )
        result.append(value)

    return result


def calculate_rsi(values, index):
    changes = [
        values[i] - values[i - 1]
        for i in range(index - 13, index + 1)
    ]

    gains = [max(x, 0) for x in changes]
    losses = [max(-x, 0) for x in changes]

    avg_gain = sum(gains) / 14
    avg_loss = sum(losses) / 14

    if avg_loss == 0:
        return 100 if avg_gain > 0 else 50

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


def backtest(symbol):
    data = get_candles(symbol)

    o = data["open"]
    h = data["high"]
    l = data["low"]
    c = data["close"]
    v = data["volume"]

    ema20 = calculate_ema(c, 20)
    ema50 = calculate_ema(c, 50)

    trades = []
    i = 50

    while i < len(c) - 1:

        rsi_value = calculate_rsi(c, i)

        avg_volume = sum(v[i-20:i]) / 20
        volume_ratio = (
            v[i] / avg_volume
            if avg_volume > 0 else 0
        )

        previous_high = max(h[i-20:i])

        signal = (
            ema20[i] > ema50[i]
            and c[i] > ema20[i]
            and 50 <= rsi_value <= 65
            and volume_ratio >= 1.5
            and c[i] > previous_high
        )

        if not signal:
            i += 1
            continue

        # Entry pada pembukaan candle berikutnya
        entry_index = i + 1
        entry = o[entry_index]

        sl = entry * (1 - STOP_LOSS)
        tp = entry * (1 + TAKE_PROFIT)

        exit_price = c[-1]
        exit_index = len(c) - 1
        outcome = "END"

        for j in range(entry_index, len(c)):

            # Antisipasi gap harga
            if o[j] <= sl:
                exit_price = o[j]
                exit_index = j
                outcome = "SL"
                break

            if o[j] >= tp:
                exit_price = o[j]
                exit_index = j
                outcome = "TP"
                break

            # Jika kedua level tersentuh dalam satu candle,
            # gunakan asumsi konservatif: SL lebih dahulu
            if l[j] <= sl:
                exit_price = sl
                exit_index = j
                outcome = "SL"
                break

            if h[j] >= tp:
                exit_price = tp
                exit_index = j
                outcome = "TP"
                break

        gross_return = (exit_price / entry) - 1
        net_return = gross_return - COST

        trades.append({
            "result": outcome,
            "return": net_return
        })

        # Tidak membuka posisi baru sebelum posisi selesai
        i = exit_index + 1

    total = len(trades)

    if total == 0:
        print(symbol, "| Belum ada transaksi")
        return

    wins = sum(
        1 for t in trades if t["return"] > 0
    )

    losses = total - wins

    win_rate = wins / total * 100

    avg_return = (
        sum(t["return"] for t in trades) / total
    ) * 100

    total_return = (
        __import__("math").prod(
            1 + t["return"] for t in trades
        ) - 1
    ) * 100

    print("\n========================")
    print("COIN:", symbol)
    print("Total trades:", total)
    print("Wins:", wins)
    print("Losses:", losses)
    print("Win rate:", round(win_rate, 2), "%")
    print("Average net:", round(avg_return, 3), "%")
    print("Compounded return:", round(total_return, 2), "%")
    print("========================")


print("=== SMART STRATEGY BACKTEST ===")
print("Timeframe: 1H")
print("Historical candles: 500")
print("SL: 2% | TP: 4%")
print("Biaya + slippage asumsi: 0.3% round trip")

for coin in COINS:
    try:
        backtest(coin)
    except Exception as e:
        print("ERROR", coin, ":", e)

    time.sleep(0.3)

print("\nBACKTEST SELESAI")

