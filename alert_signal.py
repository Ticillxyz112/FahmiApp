
import requests
import time

# ISI DENGAN DATA BOT TELEGRAM MILIKMU
TOKEN = "9119902944:AAG6_juafd16gYAtgSlPaE1s_OrpPDI2aXQ"
CHAT_ID = "1673088357"

SYMBOL = "BTCUSDT"

def ambil_data():
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": SYMBOL,
        "interval": "1h",
        "limit": 100
    }

    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()

    data = r.json()

    # Abaikan candle yang masih berjalan
    return [float(x[4]) for x in data[:-1]]

def hitung_ema(data, periode):
    ema = data[0]
    alpha = 2 / (periode + 1)

    for harga in data[1:]:
        ema = harga * alpha + ema * (1 - alpha)

    return ema

def hitung_rsi(data, periode=14):
    perubahan = [
        data[i] - data[i-1]
        for i in range(len(data)-periode, len(data))
    ]

    naik = [x for x in perubahan if x > 0]
    turun = [-x for x in perubahan if x < 0]

    avg_naik = sum(naik) / periode
    avg_turun = sum(turun) / periode

    if avg_turun == 0:
        return 100

    rs = avg_naik / avg_turun
    return 100 - (100 / (1 + rs))

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": pesan
    }

    r = requests.post(url, data=data, timeout=15)
    r.raise_for_status()

    if not r.json().get("ok"):
        raise Exception("Telegram gagal mengirim pesan")

def main():
    harga = ambil_data()

    ema20 = hitung_ema(harga[-60:], 20)
    ema50 = hitung_ema(harga, 50)
    rsi = hitung_rsi(harga)

    harga_terakhir = harga[-1]

    print("SYMBOL:", SYMBOL)
    print("Harga:", harga_terakhir)
    print("EMA20:", round(ema20, 2))
    print("EMA50:", round(ema50, 2))
    print("RSI:", round(rsi, 2))

    if (
        ema20 > ema50
        and harga_terakhir > ema20
        and 50 <= rsi <= 65
    ):
        pesan = f"""
🚨 CRYPTO BUY CANDIDATE

Coin: {SYMBOL}
Harga: {harga_terakhir}
EMA20: {round(ema20, 2)}
EMA50: {round(ema50, 2)}
RSI: {round(rsi, 2)}

Sinyal untuk diperiksa lebih lanjut.
Jangan entry tanpa konfirmasi dan manajemen risiko.
"""
        kirim_telegram(pesan)
        print("BUY CANDIDATE — Telegram terkirim!")

    else:
        print("WAIT — Belum ada sinyal.")

try:
    main()
except Exception as e:
    print("Terjadi error:", e)

