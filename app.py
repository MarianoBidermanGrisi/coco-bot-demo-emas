# app.py - Bot EMA 4/9 para Render (con logs intensivos)
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
# 🔐 Logging (más detallado)
# ===============================
logging.basicConfig(
    level=logging.DEBUG,  # Cambiado a DEBUG para ver todo
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ===============================
# 🔐 Variables de entorno
# ===============================
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logger.debug(f"🔹 BINANCE_API_KEY: {BINANCE_API_KEY[:10]}...")  # Solo muestra los primeros 10 caracteres
logger.debug(f"🔹 TELEGRAM_TOKEN: {TELEGRAM_TOKEN[:10]}...")
logger.debug(f"🔹 TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")

if not all([BINANCE_API_KEY, BINANCE_API_SECRET, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
    logger.error("❌ Faltan variables de entorno. Configúralas en Render.")
    sys.exit(1)

try:
    TELEGRAM_CHAT_ID = int(TELEGRAM_CHAT_ID)
except ValueError:
    logger.error("❌ TELEGRAM_CHAT_ID debe ser un número entero.")
    sys.exit(1)

# ===============================
# 🌐 Inicializar clientes (con try-except)
# ===============================
try:
    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    logger.info("✅ Conexión con Binance: OK")
except Exception as e:
    logger.error(f"❌ Error al conectar con Binance: {e}")
    sys.exit(1)

try:
    from telegram import Bot
    bot = Bot(token=TELEGRAM_TOKEN)
    logger.info("✅ Bot de Telegram: inicializado")
except Exception as e:
    logger.error(f"❌ Error al inicializar Telegram Bot: {e}")
    sys.exit(1)

# ===============================
# ⚙️ Configuración
# ===============================
SYMBOLS = ["DOGEUSDT", "XRPUSDT", "ETHUSDT", "AVAXUSDT", "TRXUSDT", "XLMUSDT", "SOLUSDT"]
TIMEFRAMES = ["1m", "3m", "5m", "15m"]
DATA_LIMIT = 100
MIN_CONFLUENCIA = 2

# ===============================
# 📥 Descargar datos
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
        logger.debug(f"📊 Datos descargados para {symbol} ({interval}): {len(df)} filas")
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
# 💬 Enviar alerta por Telegram
# ===============================
async def enviar_alerta_telegram(mensaje: str):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensaje, parse_mode='Markdown')
        logger.info("✅ Alerta enviada por Telegram")
    except Exception as e:
        logger.error(f"❌ Error en Telegram: {e}")

# ===============================
# 🌐 Flask
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
        if "✅" in res or "🟢" in res:
            clase = "success"
        elif "❌" in res or "🔴" in res:
            clase = "error"
        else:
            clase = "info"
        resultados_html += f'<div class="log {clase}">{res}</div>\n'

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>EMA 4/9 Bot</title>
        <meta http-equiv="refresh" content="45">
        <style>
            body {{ font-family: Arial; margin: 20px; background: #f9f9f9; }}
            .log {{ padding: 10px; margin: 8px 0; border-radius: 4px; border-left: 4px solid #007BFF; background: #fff; }}
            .log.success {{ border-left-color: #28a745; background: #d4edda; }}
            .log.error {{ border-left-color: #dc3545; background: #f8d7da; }}
            .log.info {{ border-left-color: #17a2b8; background: #d1ecf1; }}
        </style>
    </head>
    <body>
        <h1>📈 Bot EMA 4/9 - Render</h1>
        <div class="log info">Última ejecución: {ultimo_estado["fecha"]}</div>
        {resultados_html}
        <div class="log info">Estado: {ultimo_estado["mensaje"] or "Esperando..."}</div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/health')
def health():
    return {"status": "ok"}

# ===============================
# 🔁 Análisis principal
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
            logger.debug(f"🔍 Analizando {symbol} en {tf}...")
            df = descargar_datos(symbol, tf, DATA_LIMIT)
            if df is None:
                continue

            df = detectar_cruce_ema(df)
            precio_actual = df['close'].iloc[-1]

            if df['cruce_arriba'].iloc[-1]:
                cruces_compra.append(tf)
                logger.info(f"🟢 Cruce arriba en {symbol} ({tf})")
            elif df['cruce_abajo'].iloc[-1]:
                cruces_venta.append(tf)
                logger.info(f"🔴 Cruce abajo en {symbol} ({tf})")

        if precio_actual is None:
            ultimo_estado["resultados"].append(f"⚠️ {symbol}: Sin datos")
            continue

        if len(cruces_compra) >= MIN_CONFLUENCIA:
            mensaje = f"🟢 *SEÑAL DE COMPRA - EMA 4/9*\n*Par:* `{symbol}`\n*Precio:* `${precio_actual:,.6f}`\n*Timeframes:* `{', '.join(cruces_compra)}`\n*Fecha:* {ahora.strftime('%Y-%m-%d %H:%M:%S')}"
            logger.info(f"✅ COMPRA en {symbol} ({', '.join(cruces_compra)})")
            ultimo_estado["resultados"].append(f"✅ COMPRA: {symbol} en {', '.join(cruces_compra)}")
            asyncio.run(enviar_alerta_telegram(mensaje))

        elif len(cruces_venta) >= MIN_CONFLUENCIA:
            mensaje = f"🔴 *SEÑAL DE VENTA - EMA 4/9*\n*Par:* `{symbol}`\n*Precio:* `${precio_actual:,.6f}`\n*Timeframes:* `{', '.join(cruces_venta)}`\n*Fecha:* {ahora.strftime('%Y-%m-%d %H:%M:%S')}"
            logger.info(f"❌ VENTA en {symbol} ({', '.join(cruces_venta)})")
            ultimo_estado["resultados"].append(f"❌ VENTA: {symbol} en {', '.join(cruces_venta)}")
            asyncio.run(enviar_alerta_telegram(mensaje))

        else:
            ultimo_estado["resultados"].append(f"🟡 {symbol}: Sin confluencia")

# ===============================
# ▶️ Inicio del sistema
# ===============================
if __name__ == "__main__":
    logger.info("🚀 Bot EMA 4/9 iniciado. Preparando servidor...")

    def loop_analisis():
        time.sleep(5)
        logger.info("🔄 Hilo de análisis iniciado")
        while True:
            try:
                logger.debug("🔁 Iniciando ciclo de análisis...")
                ejecutar_analisis()
            except Exception as e:
                logger.error(f"❌ Error en el bucle de análisis: {e}")
            time.sleep(45)

    analizador_thread = Thread(target=loop_analisis, daemon=True)
    analizador_thread.start()

    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

