"""
Configuración de variables de entorno para el Bot de Trading
Incluye todas las configuraciones necesarias para Binance y otros servicios
"""
import os
from typing import Dict, Any, Optional

class EnvironmentConfig:
"""Maneja todas las configuraciones de variables de entorno"""

def __init__(self):
"""Inicializa la configuración de entorno"""
self.config = self._load_config()

def _load_config(self) -> Dict[str, Any]:
"""Carga todas las configuraciones"""
return {
# ============================
# CONFIGURACIONES DE BINANCE
# ============================
'BINANCE_API_KEY': self._get_env('BINANCE_API_KEY', ''),
'BINANCE_SECRET_KEY': self._get_env('BINANCE_SECRET_KEY', ''),
'BINANCE_TESTNET': self._get_env('BINANCE_TESTNET', 'true').lower() == 'true',

# ============================
# CONFIGURACIONES DE # ============================
TELEGRAM
'TELEGRAM_BOT_TOKEN': self._get_env('TELEGRAM_BOT_TOKEN', ''),
'TELEGRAM_CHAT_ID': self._get_env('TELEGRAM_CHAT_ID', ''),
'TELEGRAM_ENABLED': self._get_env('TELEGRAM_ENABLED', 'false').lower() == 'true',

# ============================
# CONFIGURACIONES DE TRADING
# ============================
'TRADING_ENABLED': self._get_env('TRADING_ENABLED', 'true').lower() == 'true',
'SYMBOLS': self._get_env('SYMBOLS', 'BTCUSDT,ETHUSDT').split(','),
'TIMEFRAMES': self._get_env('TIMEFRAMES', '1m,5m,15m').split(','),
'MAX_OPERATIONS': int(self._get_env('MAX_OPERATIONS', '3')),
'RISK_PERCENT': float(self._get_env('RISK_PERCENT', '2.0')),

# ============================
# CONFIGURACIONES DE LOGGING
# ============================
'LOG_LEVEL': self._get_env('LOG_LEVEL', 'INFO'),
'LOG_TO_FILE': self._get_env('LOG_TO_FILE', 'true').lower() == 'true',

# ============================
# CONFIGURACIONES DE RENDER
# ============================
'PORT': int(self._get_env('PORT', '10000')),
'HEALTH_CHECK_INTERVAL': int(self._get_env('HEALTH_CHECK_INTERVAL', '60')),

# ============================
# CONFIGURACIONES DE OPTIMIZACIÓN
# ============================
'AUTO_OPTIMIZE': self._get_env('AUTO_OPTIMIZE', 'true').lower() == 'true',
'OPTIMIZATION_INTERVAL': int(self._get_env('OPTIMIZATION_INTERVAL', '24')),
'MIN_SAMPLES_OPTIMIZATION': int(self._get_env('MIN_SAMPLES_OPTIMIZATION', '30')),
}

def _get_env(self, key: str, default: str = '') -> str:
"""Obtiene variable de entorno con valor por defecto"""
return os.environ.get(key, default)

def get(self, key: str, default: Any = None) -> Any:
"""Obtiene valor de configuración"""
return self.config.get(key, default)

def is_configured(self) -> bool:
"""Verifica si las configuraciones críticas están presentes"""
required_configs = [
'BINANCE_API_KEY',
'BINANCE_SECRET_KEY'
]

missing = []
for config in required_configs:
if not self.config.get(config):
missing.append(config)

if missing:
print(f"❌ Configuraciones faltantes: {', '.join(missing)}")
return False

return True

def print_configuration_summary(self):
"""Imprime resumen de la configuración"""
print("=" * 60)
print("🤖 CONFIGURACIÓN DEL BOT DE TRADING")
print("=" * 60)

print(f"🔑 Binance API: {'✅ Configurado' if self.config['BINANCE_API_KEY'] else '❌ No configurado'}")
print(f"🤖 Trading Bot: {'✅ Habilitado' if self.config['TRADING_ENABLED'] else '❌ Deshabilitado'}")
print(f"📱 Telegram: {'✅ Habilitado' if self.config['TELEGRAM_ENABLED'] else '❌ Deshabilitado'}")
print(f"🧪 Testnet: {'✅ Habilitado' if self.config['BINANCE_TESTNET'] else '❌ Deshabilitado'}")
print(f"⚙️ Auto-optimización: {'✅ Habilitada' if self.config['AUTO_OPTIMIZE'] else '❌ Deshabilitada'}")

print(f"📊 Símbolos: {', '.join(self.config['SYMBOLS'])}")
print(f"⏰ Timeframes: {', '.join(self.config['TIMEFRAMES'])}")
print(f"💰 Riesgo por operación: {self.config['RISK_PERCENT']}%")
print(f"📈 Máximo operaciones simultáneas: {self.config['MAX_OPERATIONS']}")

print("=" * 60)

def get_binance_config(self) -> Dict[str, Any]:
"""Obtiene configuración específica de Binance"""
return {
'api_key': self.config['BINANCE_API_KEY'],
'secret_key': self.config['BINANCE_SECRET_KEY'],
'testnet': self.config['BINANCE_TESTNET']
}

def get_trading_config(self) -> Dict[str, Any]:
"""Obtiene configuración específica de trading"""
return {
'symbols': self.config['SYMBOLS'],
'timeframes': self.config['TIMEFRAMES'],
'max_operations': self.config['MAX_OPERATIONS'],
'risk_percent': self.config['RISK_PERCENT'],
'enabled': self.config['TRADING_ENABLED']
}

def get_telegram_config(self) -> Dict[str, Any]:
"""Obtiene configuración específica de Telegram"""
return {
'bot_token': self.config['TELEGRAM_BOT_TOKEN'],
'chat_id': self.config['TELEGRAM_CHAT_ID'],
'enabled': self.config['TELEGRAM_ENABLED']
}

# Instancia global de configuración
env_config = EnvironmentConfig()

def get_env_manager():
"""Obtiene el manager de configuración de entorno"""
return env_config

def get_trading_config():
"""Obtiene configuración de trading"""
return env_config.get_trading_config()

def get_binance_config():
"""Obtiene configuración de Binance"""
return env_config.get_binance_config()

def get_telegram_config():
"""Obtiene configuración de Telegram"""
return env_config.get_telegram_config()

def is_trading_enabled() -> bool:
"""Verifica si el trading está habilitado"""
return env_config.get('TRADING_ENABLED', False)

def is_telegram_enabled() -> bool:
"""Verifica si Telegram está habilitado"""
return env_config.get('TELEGRAM_ENABLED', False)

def is_binance_configured() -> bool:
"""Verifica si Binance está configurado"""
api_key = env_config.get('BINANCE_API_KEY', '')
secret_key = env_config.get('BINANCE_SECRET_KEY', '')
return bool(api_key and secret_key)

# Variables de entorno requeridas
REQUIRED_ENV_VARS = [
'BINANCE_API_KEY',
'BINANCE_SECRET_KEY'
]

# Variables de entorno opcionales
OPTIONAL_ENV_VARS = [
'TELEGRAM_BOT_TOKEN',
'TELEGRAM_CHAT_ID',
'SYMBOLS',
'TIMEFRAMES',
'MAX_OPERATIONS',
'RISK_PERCENT',
'TRADING_ENABLED',
'TELEGRAM_ENABLED',
'BINANCE_TESTNET',
'AUTO_OPTIMIZE',
'LOG_LEVEL'
]

if __name__ == '__main__':
# Script de prueba
print("🔍 Verificando configuración...")

if env_config.is_configured():
print("✅ Configuración completa")
env_config.print_configuration_summary()
else:
print("❌ Configuración incompleta")
print("

📝 Variables de entorno requeridas:")
for var in REQUIRED_ENV_VARS:
print(f"  - {var}")
print("

⚙️ Variables de entorno opcionales:")
for var in OPTIONAL_ENV_VARS:
print(f"  - {var}")
