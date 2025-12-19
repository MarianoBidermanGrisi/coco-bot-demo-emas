"""
Configuraciones del Bot de Trading
Todas las constantes y configuraciones del sistema
"""

import os
from typing import List, Dict, Any

# ============================
# CONFIGURACIONES PRINCIPALES
# ============================

# Símbolos de trading
DEFAULT_SYMBOLS: List[str] = [
    'BTCUSDT', 'ETHUSDT', 'DOTUSDT', 'LINKUSDT', 'BNBUSDT', 'XRPUSDT', 
    'SOLUSDT', 'AVAXUSDT', 'DOGEUSDT', 'LTCUSDT', 'ATOMUSDT', 'XLMUSDT', 
    'ALGOUSDT', 'VETUSDT', 'ICPUSDT', 'FILUSDT', 'BCHUSDT', 'EOSUSDT', 
    'TRXUSDT', 'XTZUSDT', 'SUSHIUSDT', 'COMPUSDT', 'YFIUSDT', 'ETCUSDT', 
    'SNXUSDT', 'RENUSDT', '1INCHUSDT', 'NEOUSDT', 'ZILUSDT', 'HOTUSDT', 
    'ENJUSDT', 'ZECUSDT'
]

# Timeframes disponibles (ordenados por prioridad)
DEFAULT_TIMEFRAMES: List[str] = ['1m', '3m', '5m', '15m', '30m']

# Número de velas para análisis
DEFAULT_VELAS_OPTIONS: List[int] = [80, 100, 120, 150, 200]

# ============================
# PARÁMETROS DE ESTRATEGIA
# ============================

# Ancho mínimo del canal para considerar válido
MIN_CHANNEL_WIDTH_PERCENT: float = 4.0

# Umbrales de tendencia
TREND_THRESHOLD_DEGREES: float = 16.0
MIN_TREND_STRENGTH_DEGREES: float = 16.0

# Margen de entrada
ENTRY_MARGIN: float = 0.001

# Ratio riesgo/beneficio mínimo
MIN_RR_RATIO: float = 1.2

# ============================
# CONFIGURACIONES DE SCAN
# ============================

# Intervalo entre scans (en minutos)
SCAN_INTERVAL_MINUTES: int = 1

# Prioridad de timeframes para optimización
TIMEFRAME_PRIORITY: Dict[str, int] = {
    '1m': 200, '3m': 150, '5m': 120, '15m': 100, '30m': 80
}

# ============================
# OPTIMIZACIÓN AUTOMÁTICA
# ============================

AUTO_OPTIMIZE: bool = True
MIN_SAMPLES_OPTIMIZACION: int = 30
REEVALUACION_HORAS: int = 24
REOPTIMIZACION_OPERACIONES: int = 8

# ============================
# CONFIGURACIONES DE TELEGRAM
# ============================

# Chat IDs por defecto (pueden venir de variables de entorno)
DEFAULT_CHAT_IDS: List[str] = ['-1002272872445']

# ============================
# CONFIGURACIONES DE ARCHIVOS
# ============================

# Paths de archivos de datos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Crear directorios si no existen
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Archivos de datos
OPERACIONES_LOG_FILE = os.path.join(DATA_DIR, 'operaciones_log_v23.csv')
ESTADO_BOT_FILE = os.path.join(DATA_DIR, 'estado_bot_v23.json')
ULTIMO_REPORTE_FILE = os.path.join(DATA_DIR, 'ultimo_reporte.txt')
MEJORES_PARAMETROS_FILE = os.path.join(DATA_DIR, 'mejores_parametros.json')

# ============================
# CONFIGURACIONES DE BINANCE API
# ============================

# URLs de la API
BINANCE_BASE_URL = "https://api.binance.com"
BINANCE_WS_URL = "wss://stream.binance.com:9443"

# Timeouts y reintentos
API_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 1

# ============================
# CONFIGURACIONES DE GRÁFICOS
# ============================

# Configuración de matplotlib
MATPLOTLIB_BACKEND = 'Agg'
CHART_DPI = 100
CHART_FIGURE_SIZE = (14, 10)
CHART_STYLE = 'nightclouds'

# ============================
# CONFIGURACIONES DE RENDER
# ============================

# Puerto por defecto
DEFAULT_PORT = 5000

# Health check endpoint
HEALTH_CHECK_PATH = '/health'
WEBHOOK_PATH = '/webhook'

# ============================
# CONFIGURACIONES DE LOGGING
# ============================

LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE_FORMAT = 'trading_bot_%Y%m%d.log'

# ============================
# STOCHASTIC CONFIGURATION
# ============================

STOCH_PERIOD = 14
STOCH_K_PERIOD = 3
STOCH_D_PERIOD = 3

# Niveles de Stochastic
STOCH_OVERSOLD = 20
STOCH_OVERBOUGHT = 80
STOCH_ENTRY_OVERSOLD = 30
STOCH_ENTRY_OVERBOUGHT = 70

# ============================
# BREAKOUT CONFIGURATION
# ============================

# Tiempo máximo para esperar reentry (en minutos)
BREAKOUT_TIMEOUT_MINUTES = 30
BREAKOUT_MIN_INTERVAL_MINUTES = 25  # Mínimo entre breakouts del mismo símbolo

# ============================
# ERRORES Y EXCEPCIONES
# ============================

class TradingBotError(Exception):
    """Excepción base para el bot de trading"""
    pass

class ConfigurationError(TradingBotError):
    """Error de configuración"""
    pass

class APIConnectionError(TradingBotError):
    """Error de conexión con API"""
    pass

class DataProcessingError(TradingBotError):
    """Error procesando datos"""
    pass

class StrategyError(TradingBotError):
    """Error en la estrategia de trading"""
    pass