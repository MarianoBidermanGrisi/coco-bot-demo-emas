"""
Archivo Principal del Bot de Trading
Punto de entrada que conecta todos los módulos del sistema
"""

import sys
import os
import time
import threading
import logging
from datetime import datetime

# Agregar el directorio src al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar módulos del sistema
from config.environment import get_env_manager, get_trading_config, get_file_config
from config.settings import *
from utils.logging_manager import setup_logging, get_logger
from apiBinance.binance_client import get_binance_client
from apiBinance.market_data import get_market_data_manager
from bot.telegram_bot import get_telegram_bot
from bot.signal_generator import get_signal_generator
from bot.operation_manager import get_operation_manager
from utils.state_manager import get_state_manager
from api.health_check import get_health_check_api

# Importar estrategias (mantener la lógica original intacta)
from strategies.breakout_reentry_strategy import TradingBot
from strategies.trading_optimizer import OptimizadorIA

# Configurar logging
setup_logging()
logger = get_logger(__name__)

class TradingBotMain:
    """Clase principal del bot de trading"""
    
    def __init__(self):
        """Inicializa el bot principal"""
        try:
            logger.info("🚀 Inicializando TradingBotMain...")
            
            # Inicializar componentes
            self.env_manager = get_env_manager()
            self.binance_client = get_binance_client()
            self.market_data_manager = get_market_data_manager()
            self.telegram_bot = get_telegram_bot()
            self.signal_generator = get_signal_generator()
            self.operation_manager = get_operation_manager()
            self.state_manager = get_state_manager()
            self.health_check_api = get_health_check_api()
            
            # Cargar configuración
            self.trading_config = get_trading_config()
            self.file_config = get_file_config()
            
            # Combinar configuraciones
            self.config = {**self.trading_config, **self.file_config}
            
            # Inicializar bot de trading con estrategia original
            self.trading_bot = TradingBot(self.config)
            
            self.is_running = False
            self.bot_thread = None
            
            logger.info("✅ TradingBotMain inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando TradingBotMain: {e}")
            raise
    
    def test_connections(self) -> bool:
        """Prueba todas las conexiones del sistema"""
        try:
            logger.info("🔍 Probando conexiones del sistema...")
            
            # Probar configuración
            if not self.env_manager.is_configured():
                logger.error("❌ Configuración incompleta")
                return False
            
            # Probar Binance
            if not self.binance_client.test_connection():
                logger.error("❌ Error conectando con Binance")
                return False
            
            # Probar Telegram (opcional)
            if self.telegram_bot.is_enabled():
                if not self.telegram_bot.test_connection():
                    logger.warning("⚠️ Error conectando con Telegram (continuando sin Telegram)")
            
            logger.info("✅ Todas las conexiones probadas correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error probando conexiones: {e}")
            return False
    
    def run_health_check_api(self):
        """Ejecuta la API de health check en hilo separado"""
        try:
            logger.info("🏥 Iniciando Health Check API...")
            self.health_check_api.run(host='0.0.0.0', port=5000, debug=False)
        except Exception as e:
            logger.error(f"❌ Error en Health Check API: {e}")
    
    def run_trading_bot(self):
        """Ejecuta el bot de trading en hilo separado"""
        try:
            logger.info("🤖 Iniciando Trading Bot...")
            self.trading_bot.iniciar()
        except Exception as e:
            logger.error(f"❌ Error en Trading Bot: {e}")
    
    def start(self):
        """Inicia el sistema completo"""
        try:
            logger.info("=" * 70)
            logger.info("🤖 BOT DE TRADING - BREAKOUT + REENTRY")
            logger.info("=" * 70)
            
            # Mostrar configuración
            self.env_manager.print_configuration_summary()
            
            # Probar conexiones
            if not self.test_connections():
                logger.error("❌ Error en conexiones, abortando inicio")
                return False
            
            # Marcar como ejecutándose
            self.is_running = True
            
            # Iniciar Health Check API en hilo separado
            api_thread = threading.Thread(target=self.run_health_check_api, daemon=True)
            api_thread.start()
            
            # Dar tiempo a la API para inicializar
            time.sleep(2)
            
            logger.info("✅ Sistema iniciado correctamente")
            logger.info("📊 Health Check: http://localhost:5000/health")
            logger.info("📈 Status: http://localhost:5000/status")
            
            # Iniciar bot de trading (esto bloquea)
            self.run_trading_bot()
            
            return True
            
        except KeyboardInterrupt:
            logger.info("🛑 Deteniendo bot por solicitud del usuario")
            return True
        except Exception as e:
            logger.error(f"❌ Error en start: {e}")
            return False
        finally:
            self.is_running = False
    
    def stop(self):
        """Detiene el sistema"""
        try:
            logger.info("🛑 Deteniendo sistema...")
            self.is_running = False
            
            # Guardar estado final
            if hasattr(self, 'trading_bot'):
                self.trading_bot.guardar_estado()
            
            logger.info("👋 Sistema detenido")
            
        except Exception as e:
            logger.error(f"❌ Error deteniendo sistema: {e}")

def main():
    """Función principal"""
    try:
        # Crear instancia del bot principal
        bot_main = TradingBotMain()
        
        # Iniciar sistema
        success = bot_main.start()
        
        if not success:
            logger.error("❌ El bot no pudo iniciarse correctamente")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal en main: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()