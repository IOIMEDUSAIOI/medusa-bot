import time
import requests
import yfinance as yf
import pandas as pd
import ta

TELEGRAM_TOKEN = "8625476527:AAEdnivZyE9tkP_trLVKQr3TpsZ4lxO3dWY"
TELEGRAM_CHAT_ID = "1767699298"

PRIORITY_TICKERS = [
    "NVDA", "RDDT", "AAPL", "MSFT", "META", "GOOGL", "AMZN", "PLTR", "AMD", "TSLA"
]

SECONDARY_TICKERS = [
    "MARA", "DELL", "XIACY", "BLK", "NDAQ", "MSTR", "LLY", "COST", "BROS", 
    "BYDDY", "UUUU", "RIOT", "MICC", "KGC", "SPOT", "SNDK", "HUT", "PLUG"
]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram hatasi: {e}")

def analyze_ticker(symbol):
    # Veri çekimini daha stabil parametrelerle yapıyoruz (period=1mo yerine 1d/5d)
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="5d", interval="15m")
    
    if df.empty or len(df) < 15:
        # Alternatif veri denemesi (Günlük veri fallback)
        df = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < 15:
            return None

    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    df['EMA_20'] = ta.trend.ema_indicator(df['Close'], window=20)
    df['EMA_50'] = ta.trend.ema_indicator(df['Close'], window=50)

    last_price = float(df['Close'].iloc[-1])
    last_rsi = float(df['RSI'].iloc[-1])
    last_ema20 = float(df['EMA_20'].iloc[-1])
    last_ema50 = float(df['EMA_50'].iloc[-1])

    signal = "NOTR ⚖️"
    if last_rsi < 30 and last_price > last_ema20:
        signal = "GUCLU AL / DIP 🚀"
    elif last_rsi > 70:
        signal = "SAT / DUZELTME ⚠️"
    elif last_price > last_ema20 and last_ema20 > last_ema50:
        signal = "YUKSELIS TRENDI 📈"
    elif last_price < last_ema20 and last_ema20 < last_ema50:
        signal = "DUSUS TRENDI 📉"

    return (
        f"📊 *{symbol} HISSE ANALIZI*\n"
        f"💵 *Anlik Fiyat:* ${last_price:.2f}\n"
        f"📈 *Sinyal:* {signal}\n\n"
        f"🔍 *Teknik Gostergeler:*\n"
        f"• RSI (14): {last_rsi:.1f}\n"
        f"• EMA 20: ${last_ema20:.2f}\n"
        f"• EMA 50: ${last_ema50:.2f}"
    )

def run_priority_scan():
    send_telegram_message("⚡ *[15 DK LIK TARAMA]* Öncelikli Hisseler Taranıyor...")
    for symbol in PRIORITY_TICKERS:
        try:
            report = analyze_ticker(symbol)
            if report:
                send_telegram_message(report)
                time.sleep(1)
        except Exception as e:
            print(f"{symbol} hatasi: {e}")

def run_secondary_scan(tag_name):
    send_telegram_message(f"🔔 *[{tag_name}]* Genel Portföy Taranıyor...")
    for symbol in SECONDARY_TICKERS:
        try:
            report = analyze_ticker(symbol)
            if report:
                send_telegram_message(report)
                time.sleep(1)
        except Exception as e:
            print(f"{symbol} hatasi: {e}")

def main():
    print("Bot aktif, taramalar basliyor...")
    send_telegram_message("🤖 *Medusa Borsa Asistani Aktif!*")
    
    counter = 0
    while True:
        run_priority_scan()
        if counter % 32 == 0:
            tag = "GUN ACILISI" if counter == 0 else "GUN KAPANISI"
            run_secondary_scan(tag)
        counter += 1
        time.sleep(900)

if __name__ == "__main__":
    main()
        
