# app.py - Bot de Cruce EMA 4/9 con Binance + Telegram + Render
import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime
import time
import os
import asyncio
from flask import Flask, render_template_string
from threading import Thread
import logging
import sys

# ===============================
# 🔐 Logging
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ===============================
# 🔐 Binance & Telegram
# ===============================
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "oCYyOTBPPLr2ggLx8yszPRjSWxEecNQIL7U2iFPyhDTwsXNcD3otGMo1FtOdotHA")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "9qtqNGYJSQqJPVQPaRLt0vYbRo4IPnSj3hby1sRUoWBbhqI4ETfRvsNPHyyZbflx")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7969091726:AAFVTZAlWN0aA6uMtJgWfnQhzTRD3cpx4wM")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "1570204748"))

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

# ===============================
# ⚙️ Configuración
# ===============================
SYMBOLS = ["DOGEUSDT", "XRPUSDT", "ETHUSDT", "AVAXUSDT", "TRXUSDT", "XLMUSDT", "SOLUSDT"]
TIMEFRAMES = ["1m", "3m", "5m", "15m"]
DATA_LIMIT = 100
MIN_CONFLUENCIA = 2  # Mínimo de timeframes con cruce para enviar alerta

# ===============================
# 📥 Descargar datos desde Binance
# ===============================
def descargar_datos(symbol: str, interval: str, limit: int):
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
        ])
        df['close'] = pd.to_numeric(df['close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df if len(df) >= 10 else None
    except Exception as e:
        logger.warning(f"⚠️ Error descargando {symbol} ({interval}): {e}")
        return None

# ===============================
# 📊 Detectar cruce EMA 4/9
# ===============================
def detectar_cruce_ema(df):
    df = df.copy()
    df['ema4'] = df['close'].ewm(span=4, adjust=False).mean()
    df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['cruce_arriba'] = (df['ema4'] > df['ema9']) & (df['ema4'].shift(1) <= df['ema9'].shift(1))
    df['cruce_abajo'] = (df['ema4'] < df['ema9']) & (df['ema4'].shift(1) >= df['ema9'].shift(1))
    return df

# ===============================
# 💬 Telegram Bot
# ===============================
from telegram import Bot

bot = Bot(token=TELEGRAM_TOKEN)

async def enviar_alerta_telegram(mensaje: str):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensaje, parse_mode='Markdown')
        logger.info("✅ Alerta enviada por Telegram")
    except Exception as e:
        logger.error(f"❌ Error en Telegram: {e}")

# ===============================
# 🌐 Flask Web Server (para Render)
# ===============================
app = Flask(__name__)

ultimo_estado = {
    "fecha": "",
    "resultados": [],
    "mensaje": ""
}

@app.route('/')
def index():
    resultados_html = ""
    for res in ultimo_estado["resultados"]:
        color = "success" if "✅" in res else "error"
        resultados_html += f'<div class="log {color}">{res}</div>\n'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>EMA 4/9 Bot - Estado</title>
        <meta http-equiv="refresh" content="45">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #fff; }}
            .log {{ padding: 10px; margin: 8px 0; border-radius: 4px; border-left: 4px solid #007BFF; }}
            .log.success {{ border-left-color: #28a745; color: #155724; background: #d4edda; }}
            .log.error {{ border-left-color: #dc3545; color: #721c24; background: #f8d7da; }}
            h1 {{ color: #333; }}
        </style>
    </head>
    <body>
        <h1>📈 Bot EMA 4/9 - Cruce Simple</h1>
        <div class="log"><strong>Última ejecución:</strong> {ultimo_estado["fecha"]}</div>
        {resultados_html}
        <div class="log"><strong>Estado:</strong> {ultimo_estado["mensaje"] or "Esperando..."}</div>
        <p><em>🔄 Recarga automática cada 45 segundos.</em></p>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/health')
def health():
    return {"status": "ok"}

# ===============================
# 🔁 Análisis principal (solo EMA 4/9)
# ===============================
def ejecutar_analisis():
    global ultimo_estado
    ahora = datetime.now()
    logger.info(f"\n📆 [{ahora.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando análisis EMA 4/9...")
    
    ultimo_estado["fecha"] = ahora.strftime('%Y-%m-%d %H:%M:%S')
    ultimo_estado["resultados"] = []
    ultimo_estado["mensaje"] = "Análisis completado"

    for symbol in SYMBOLS:
        cruces_compra = []
        cruces_venta = []
        precio_actual = None

        for tf in TIMEFRAMES:
            df = descargar_datos(symbol, tf, DATA_LIMIT)
            if df is None:
                continue

            df = detectar_cruce_ema(df)
            precio_actual = df['close'].iloc[-1]

            if df['cruce_arriba'].iloc[-1]:
                cruces_compra.append(tf)
            elif df['cruce_abajo'].iloc[-1]:
                cruces_venta.append(tf)

        # Solo generar señal si hay confluencia mínima
        if precio_actual is None:
            continue

        if len(cruces_compra) >= MIN_CONFLUENCIA:
            mensaje = f"""
🟢 *SEÑAL DE COMPRA - EMA 4/9*
──────────────────────────────
*Par:* `{symbol}`
*Precio:* `${precio_actual:,.6f}`
*Timeframes:* `{', '.join(cruces_compra)}`
*Confluencia:* `{len(cruces_compra)}/{len(TIMEFRAMES)}`
*Fecha:* {ahora.strftime('%Y-%m-%d %H:%M:%S')}
"""
            logger.info(f"✅ COMPRA en {symbol} ({', '.join(cruces_compra)})")
            ultimo_estado["resultados"].append(f"✅ COMPRA: {symbol} en {', '.join(cruces_compra)}")
            asyncio.run(enviar_alerta_telegram(mensaje))

        elif len(cruces_venta) >= MIN_CONFLUENCIA:
            mensaje = f"""
🔴 *SEÑAL DE VENTA - EMA 4/9*
──────────────────────────────
*Par:* `{symbol}`
*Precio:* `${precio_actual:,.6f}`
*Timeframes:* `{', '.join(cruces_venta)}`
*Confluencia:* `{len(cruces_venta)}/{len(TIMEFRAMES)}`
*Fecha:* {ahora.strftime('%Y-%m-%d %H:%M:%S')}
"""
            logger.info(f"❌ VENTA en {symbol} ({', '.join(cruces_venta)})")
            ultimo_estado["resultados"].append(f"❌ VENTA: {symbol} en {', '.join(cruces_venta)}")
            asyncio.run(enviar_alerta_telegram(mensaje))

        else:
            ultimo_estado["resultados"].append(f"🟡 {symbol}: Sin confluencia suficiente")

# ===============================
# ▶️ Inicio del sistema
# ===============================
if __name__ == "__main__":
    # Primera ejecución inmediata
    ejecutar_analisis()

    # Hilo para análisis periódico
    def loop_analisis():
        while True:
            try:
                ejecutar_analisis()
            except Exception as e:
                logger.error(f"❌ Error en el bucle: {e}")
            time.sleep(45)  # Cada 45 segundos

    Thread(target=loop_analisis, daemon=True).start()

    # Iniciar servidor web
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)