"""
Configuración de variables de entorno para el Bot de Trading
Versión simplificada para Render.com
Incluye todas las configuraciones necesarias para Binance y otros servicios
"""
import os
from typing import Dict, Any, Optional, List


class EnvironmentConfig:
    """Maneja todas las configuraciones de variables de entorno - versión simplificada"""

    def __init__(self):
        """Inicializa la configuración de entorno"""
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Carga todas las configuraciones"""
        try:
            logger.info("🔧 Cargando configuración de entorno...")
            
            config = {
                # ============================
                # CONFIGURACIONES DE BINANCE
                # ============================
                'BINANCE_API_KEY': self._get_env('BINANCE_API_KEY', ''),
                'BINANCE_SECRET_KEY': self._get_env('BINANCE_SECRET_KEY', ''),
                'BINANCE_TESTNET': self._get_env('BINANCE_TESTNET', 'true').lower() == 'true',

                # ============================
                # CONFIGURACIONES DE TELEGRAM
                # ============================
                'TELEGRAM_BOT_TOKEN': self._get_env('TELEGRAM_BOT_TOKEN', ''),
                'TELEGRAM_CHAT_ID': self._get_env('TELEGRAM_CHAT_ID', ''),
                'TELEGRAM_ENABLED': self._get_env('TELEGRAM_ENABLED', 'false').lower() == 'true',

                # ============================
                # CONFIGURACIONES DE TRADING
                # ============================
                'TRADING_ENABLED': self._get_env('TRADING_ENABLED', 'true').lower() == 'true',
                'SYMBOLS': self._parse_list_env('SYMBOLS', 'BTCUSDT,ETHUSDT'),
                'TIMEFRAMES': self._parse_list_env('TIMEFRAMES', '1m,5m,15m'),
                'MAX_OPERATIONS': self._get_int_env('MAX_OPERATIONS', 3),
                'RISK_PERCENT': self._get_float_env('RISK_PERCENT', 2.0),

                # ============================
                # CONFIGURACIONES DE LOGGING
                # ============================
                'LOG_LEVEL': self._get_env('LOG_LEVEL', 'INFO'),
                'LOG_TO_FILE': self._get_env('LOG_TO_FILE', 'true').lower() == 'true',

                # ============================
                # CONFIGURACIONES DE RENDER
                # ============================
                'PORT': self._get_int_env('PORT', 10000),
                'HEALTH_CHECK_INTERVAL': self._get_int_env('HEALTH_CHECK_INTERVAL', 60),

                # ============================
                # CONFIGURACIONES DE OPTIMIZACIÓN
                # ============================
                'AUTO_OPTIMIZE': self._get_env('AUTO_OPTIMIZE', 'true').lower() == 'true',
                'OPTIMIZATION_INTERVAL': self._get_int_env('OPTIMIZATION_INTERVAL', 24),
                'MIN_SAMPLES_OPTIMIZATION': self._get_int_env('MIN_SAMPLES_OPTIMIZATION', 30),
            }
            
            logger.info("✅ Configuración de entorno cargada correctamente")
            return config
            
        except Exception as e:
            logger.error(f"❌ Error cargando configuración: {e}")
            # Configuración por defecto en caso de error
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto en caso de error"""
        return {
            'BINANCE_API_KEY': '',
            'BINANCE_SECRET_KEY': '',
            'BINANCE_TESTNET': True,
            'TELEGRAM_BOT_TOKEN': '',
            'TELEGRAM_CHAT_ID': '',
            'TELEGRAM_ENABLED': False,
            'TRADING_ENABLED': True,
            'SYMBOLS': ['BTCUSDT', 'ETHUSDT'],
            'TIMEFRAMES': ['1m', '5m', '15m'],
            'MAX_OPERATIONS': 3,
            'RISK_PERCENT': 2.0,
            'LOG_LEVEL': 'INFO',
            'LOG_TO_FILE': True,
            'PORT': 10000,
            'HEALTH_CHECK_INTERVAL': 60,
            'AUTO_OPTIMIZE': True,
            'OPTIMIZATION_INTERVAL': 24,
            'MIN_SAMPLES_OPTIMIZATION': 30,
        }

    def _get_env(self, key: str, default: str = '') -> str:
        """Obtiene variable de entorno con valor por defecto"""
        try:
            return os.environ.get(key, default)
        except Exception:
            return default

    def _get_int_env(self, key: str, default: int) -> int:
        """Obtiene variable de entorno como entero"""
        try:
            value = os.environ.get(key)
            if value is None:
                return default
            return int(value)
        except (ValueError, TypeError):
            return default

    def _get_float_env(self, key: str, default: float) -> float:
        """Obtiene variable de entorno como float"""
        try:
            value = os.environ.get(key)
            if value is None:
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    def _parse_list_env(self, key: str, default: str) -> List[str]:
        """Parsea variable de entorno como lista"""
        try:
            value = os.environ.get(key, default)
            if not value:
                return []
            return [item.strip() for item in value.split(',') if item.strip()]
        except Exception:
            return default.split(',')

    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene valor de configuración"""
        return self.config.get(key, default)

    def is_configured(self) -> bool:
        """Verifica si las configuraciones críticas están presentes"""
        try:
            required_configs = [
                'BINANCE_API_KEY',
                'BINANCE_SECRET_KEY'
            ]
            missing = []
            for config in required_configs:
                if not self.config.get(config):
                    missing.append(config)

            if missing:
                return False
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verificando configuración: {e}")
            return False

    def print_configuration_summary(self):
        """Imprime resumen de la configuración"""
        try:
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
            print(f"🌐 Puerto: {self.config['PORT']}")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error mostrando configuración: {e}")

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

    def validate_config(self) -> Dict[str, Any]:
        """Valida la configuración y retorna reporte"""
        try:
            validation_report = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'info': []
            }

            # Validar configuraciones críticas
            if not self.config['BINANCE_API_KEY']:
                validation_report['errors'].append('BINANCE_API_KEY no configurado')
                validation_report['valid'] = False

            if not self.config['BINANCE_SECRET_KEY']:
                validation_report['errors'].append('BINANCE_SECRET_KEY no configurado')
                validation_report['valid'] = False

            # Validaciones opcionales
            if not self.config['SYMBOLS']:
                validation_report['warnings'].append('SYMBOLS no configurado, usando por defecto')

            if not self.config['TIMEFRAMES']:
                validation_report['warnings'].append('TIMEFRAMES no configurado, usando por defecto')

            # Información
            if self.config['BINANCE_TESTNET']:
                validation_report['info'].append('Usando Binance Testnet (modo seguro)')

            if self.config['TELEGRAM_ENABLED']:
                if self.config['TELEGRAM_BOT_TOKEN']:
                    validation_report['info'].append('Telegram habilitado con notificaciones')
                else:
                    validation_report['warnings'].append('TELEGRAM_ENABLED=true pero no hay TOKEN configurado')

            return validation_report
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Error validando configuración: {e}'],
                'warnings': [],
                'info': []
            }


# Configurar logger
import logging
logger = logging.getLogger(__name__)

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
    
    # Validar configuración
    validation = env_config.validate_config()
    
    if validation['valid']:
        print("✅ Configuración válida")
        env_config.print_configuration_summary()
    else:
        print("❌ Configuración inválida:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    # Mostrar warnings
    if validation['warnings']:
        print("\n⚠️ Advertencias:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    # Mostrar información
    if validation['info']:
        print("\nℹ️ Información:")
        for info in validation['info']:
            print(f"  - {info}")
    
    print("\n📝 Variables de entorno requeridas:")
    for var in REQUIRED_ENV_VARS:
        status = "✅" if env_config.get(var) else "❌"
        print(f"  {status} {var}")
    
    print("\n⚙️ Variables de entorno opcionales:")
    for var in OPTIONAL_ENV_VARS:
        value = env_config.get(var)
        print(f"  🔧 {var}: {value}")
