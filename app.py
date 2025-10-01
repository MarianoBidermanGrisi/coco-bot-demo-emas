# app.py - Bot EMA 4/9 para Render + cron-job.org (modo manual)
import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime
import os
import asyncio
import logging
import sys
from flask import Flask, render_template_string
from telegram import Bot

# ===============================
# 🔐 Logging
# ===============================
logging.basicConfig(
    level=logging.DEBUG,
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

if not all([BINANCE_API_KEY, BINANCE_API_SECRET, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
    logger.error("❌ Faltan variables de entorno.")
    sys.exit(1)

try:
    TELEGRAM_CHAT_ID = int(TELEGRAM_CHAT_ID)
except ValueError:
    logger.error("❌ TELEGRAM_CHAT_ID debe ser un número entero válido.")
    sys.exit(1)

# ===============================
# 🌐 Inicializar clientes
# ===============================
try:
    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    logger.info("✅ Conexión con Binance: OK")
except Exception as e:
    logger.error(f"❌ Error al conectar con Binance: {e}")
    sys.exit(1)

try:
    bot = Bot(token=TELEGRAM_TOKEN)
    # Loop asíncrono dedicado para Telegram
    telegram_loop = asyncio.new_event_loop()
    from threading import Thread
    Thread(target=telegram_loop.run_forever, daemon=True).start()
    logger.info("✅ Bot de Telegram inicializado")
except Exception as e:
    logger.error(f"❌ Error al inicializar Telegram: {e}")
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
# 💬 Enviar alerta a Telegram (seguro)
# ===============================
def enviar_alerta_telegram_sync(mensaje: str):
    async def _send():
        try:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensaje, parse_mode='Markdown')
            logger.info("✅ Señal enviada a Telegram")
        except Exception as e:
            logger.error(f"❌ Error al enviar a Telegram: {e}")

    future = asyncio.run_coroutine_threadsafe(_send(), telegram_loop)
    try:
        future.result(timeout=10)
    except Exception as e:
        logger.error(f"❌ Timeout al enviar mensaje: {e}")

# ===============================
# 🌐 Flask App
# ===============================
app = Flask(__name__)

ultimo_estado = {
    "fecha": "Esperando primer análisis...",
    "resultados": ["El bot aún no ha analizado."],
    "mensaje": "Esperando"
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
        <!-- Controlado por cron-job.org -->
        <style>
            body {{ font-family: Arial; margin: 20px; background: #f9f9f9; }}
            .log {{ padding: 10px; margin: 8px 0; border-radius: 4px; border-left: 4px solid #007BFF; background: #fff; }}
            .log.success {{ border-left-color: #28a745; background: #d4edda; }}
            .log.error {{ border-left-color: #dc3545; background: #f8d7da; }}
            .log.info {{ border-left-color: #17a2b8; background: #d1ecf1; }}
        </style>
    </head>
    <body>
        <h1>📈 Bot EMA 4/9 - Estado</h1>
        <div class="log info">Última ejecución: {ultimo_estado["fecha"]}</div>
        {resultados_html}
        <div class="log info">Estado: {ultimo_estado["mensaje"]}</div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/health')
def health():
    return {"status": "ok"}

@app.route('/analizar')
def ruta_analizar():
    logger.info("🔹 Ruta /analizar accedida — Iniciando análisis programado")
    ejecutar_analisis()
    return {"status": "análisis completado", "time": datetime.now().isoformat()}, 200

# ===============================
# 🔁 Análisis principal
# ===============================
def ejecutar_analisis():
    global ultimo_estado
    ahora = datetime.now()
    logger.info(f"\n📆 [{ahora.strftime('%Y-%m-%d %H:%M:%S')}] Análisis iniciado por solicitud externa")

    resultados = []
    mensaje_general = "Sin señales"

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
                logger.info(f"🟢 Cruce arriba en {symbol} ({tf})")
            elif df['cruce_abajo'].iloc[-1]:
                cruces_venta.append(tf)
                logger.info(f"🔴 Cruce abajo en {symbol} ({tf})")

        if precio_actual is None:
            resultados.append(f"⚠️ {symbol}: Sin datos")
            continue

        if len(cruces_compra) >= MIN_CONFLUENCIA:
            mensaje = (
                f"🟢 *SEÑAL DE COMPRA - EMA 4/9*\n"
                f"*Par:* `{symbol}`\n"
                f"*Precio:* `${precio_actual:,.6f}`\n"
                f"*Timeframes:* `{', '.join(cruces_compra)}`\n"
                f"*Fecha:* {ahora.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            resultados.append(f"✅ COMPRA: {symbol} en {', '.join(cruces_compra)}")
            enviar_alerta_telegram_sync(mensaje)
            mensaje_general = "Señal activa"

        elif len(cruces_venta) >= MIN_CONFLUENCIA:
            mensaje = (
                f"🔴 *SEÑAL DE VENTA - EMA 4/9*\n"
                f"*Par:* `{symbol}`\n"
                f"*Precio:* `${precio_actual:,.6f}`\n"
                f"*Timeframes:* `{', '.join(cruces_venta)}`\n"
                f"*Fecha:* {ahora.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            resultados.append(f"❌ VENTA: {symbol} en {', '.join(cruces_venta)}")
            enviar_alerta_telegram_sync(mensaje)
            mensaje_general = "Señal activa"

        else:
            resultados.append(f"🟡 {symbol}: Sin confluencia")

    # Actualizar estado global
    ultimo_estado["fecha"] = ahora.strftime('%Y-%m-%d %H:%M:%S')
    ultimo_estado["resultados"] = resultados
    ultimo_estado["mensaje"] = mensaje_general

    logger.info("✅ Análisis completado y estado actualizado")

# ===============================
# ▶️ Inicio del servidor
# ===============================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

