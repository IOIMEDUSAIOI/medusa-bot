import time
import datetime
import requests
import yfinance as yf
import pandas as pd
import ta

# --- TELEGRAM BOT BİLGİLERİ ---
TELEGRAM_TOKEN = "8625476527:AAEdnivZyE9tkP_trLVKQr3TpsZ4lxO3dWY"
TELEGRAM_CHAT_ID = "1767699298"

# 1. ÖNCELİKLİ HİSSELER (Her 15 Dakikada Bir Taranacak)
PRIORITY_TICKERS = [
    "NVDA", "RDDT", "AAPL", "MSFT", "META", "GOOGL", "AMZN", "PLTR", "AMD", "TSLA"
]

# 2. İKİNCİL HİSSELER (Günde Yalnızca 2 Kez - Açılış & Kapanışta Taranacak)
SECONDARY_TICKERS = [
    "MARA", "DELL", "XIACY", "BLK", "NDAQ", "MSTR", "LLY", "COST", "BROS", 
    "BYDDY", "UUUU", "RIOT", "MICC", "KGC", "SPOT", "SNDK", "HUT", "PLUG"
]

def send_telegram_message(message):
    """Telegram üzerinden mesaj iletir."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram mesaj hatası: {e}")

def analyze_ticker(symbol):
    """Hissenin teknik analizini ve son çıkan haberini derler."""
    ticker = yf.Ticker(symbol)
    
    # 15 dakikalık periyot için veri çekimi
    df = ticker.history(period="5d", interval="15m")
    if df.empty or len(df) < 20:
        return None

    # İndikatör Hesaplamaları
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    df['EMA_20'] = ta.trend.ema_indicator(df['Close'], window=20)
    df['EMA_50'] = ta.trend.ema_indicator(df['Close'], window=50)

    last_price = float(df['Close'].iloc[-1])
    last_rsi = float(df['RSI'].iloc[-1])
    last_ema20 = float(df['EMA_20'].iloc[-1])
    last_ema50 = float(df['EMA_50'].iloc[-1])

    # Sinyal Mantığı
    signal = "NÖTR ⚖️"
    if last_rsi < 30 and last_price > last_ema20:
        signal = "🚨 GÜÇLÜ AL / DİP SEVİYE 🚀"
    elif last_rsi > 70:
        signal = "⚠️ AŞIRI ALIM / SATIŞ RİSKİ"
    elif last_price > last_ema20 and last_ema20 > last_ema50:
        signal = "YÜKSELİŞ TRENDİ 📈"
    elif last_price < last_ema20 and last_ema20 < last_ema50:
        signal = "DÜŞÜŞ TRENDİ 📉"

    # Son Haber
    news = ticker.news
    latest_news = news[0]['title'] if news else "Güncel haber bulunamadı."

    report = (
        f"📊 *{symbol} HİSSE ANALİZİ*\n"
        f"💵 *Anlık Fiyat:* ${last_price:.2f}\n"
        f"📈 *Sinyal:* {signal}\n\n"
        f"🔍 *15 Dakikalık Göstergeler:*\n"
        f"• RSI (14): {last_rsi:.1f}\n"
        f"• EMA 20: ${last_ema20:.2f}\n"
        f"• EMA 50: ${last_ema50:.2f}\n\n"
        f"📰 *Son Haber:* {latest_news}"
    )
    return report

def run_priority_scan():
    """Öncelikli hisseleri 15 dakikada bir tarar."""
    send_telegram_message("⚡ *[15 DK LİK TARAMA]* Öncelikli Hisseler (NVDA, RDDT vb.) Güncelleniyor...")
    for symbol in PRIORITY_TICKERS:
        try:
            report = analyze_ticker(symbol)
            if report:
                send_telegram_message(report)
                time.sleep(1.5)
        except Exception as e:
            print(f"{symbol} öncelikli tarama hatası: {e}")

def run_secondary_scan(tag_name):
    """Geri kalan ikincil hisseleri günde 2 kez (Açılış/Kapanış) tarar."""
    send_telegram_message(f"🔔 *[{tag_name} RAPORU]* Genel Portföy Hisseleri Taranıyor...")
    for symbol in SECONDARY_TICKERS:
        try:
            report = analyze_ticker(symbol)
            if report:
                send_telegram_message(report)
                time.sleep(1.5)
        except Exception as e:
            print(f"{symbol} ikincil tarama hatası: {e}")

def main():
    print("Medusa Borsa Otomasyonu Başlatıldı...")
    send_telegram_message("🤖 *Medusa Akıllı Borsa Asistanı Aktif!*\n"
                          "• Öncelikli Hisseler: Her 15 dakikada bir\n"
                          "• İkincil Hisseler: Günde 2 kez (Açılış & Kapanış)")
    
    counter = 0
    while True:
        # 1. Öncelikli Hisselerin Taraması (Her Döngüde / 15 Dakikada Bir)
        run_priority_scan()
        
        # 2. İkincil Hisselerin Taraması (Her 32 Döngüde Bir ≈ Yaklaşık 8 Saatte Bir / Günde 2 Kez)
        if counter % 32 == 0:
            tag = "GÜN AÇILIŞI / İLK SEANS" if counter == 0 else "GÜN KAPANIŞI / İKİNCİ SEANS"
            run_secondary_scan(tag)
            
        counter += 1
        
        # 15 Dakika (900 saniye) Bekleme Periyodu
        time.sleep(900)

if __name__ == "__main__":
    main()
      
