"""
Servicio Web principal para Render.com
Incluye tanto la API de health check como el bot de trading
"""
import logging
import sys
import os
import threading
import time
import signal

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar el directorio actual al path para imports locales
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importar HealthCheckAPI con manejo de errores
try:
    from health_check import HealthCheckAPI
    logger.info("✅ HealthCheckAPI importado correctamente")
except ImportError as e:
    logger.error(f"❌ Error importando HealthCheckAPI: {e}")
    logger.error("Asegúrate de que health_check.py esté en el mismo directorio")
    HealthCheckAPI = None

# Importar el bot de trading con manejo de errores
try:
    # Intentar importar desde src
    if os.path.exists(os.path.join(current_dir, 'src')):
        sys.path.insert(0, os.path.join(current_dir, 'src'))
        from srcMain import TradingBotMain
        logger.info("✅ TradingBotMain importado correctamente desde src")
        TRADING_BOT_AVAILABLE = True
    else:
        logger.warning("⚠️ Directorio src no encontrado, bot de trading no disponible")
        TRADING_BOT_AVAILABLE = False
except ImportError as e:
    logger.warning(f"⚠️ Error importando TradingBotMain: {e}")
    logger.warning("El bot de trading no se iniciará")
    TRADING_BOT_AVAILABLE = False

class TradingBotService:
    """Servicio principal que combina API y bot de trading"""
    def __init__(self):
        """Inicializa el servicio completo"""
        try:
            self.health_api = None
            self.trading_bot = None
            self.is_running = False
            self.threads = []

            # Inicializar Health Check API
            self._init_health_api()

            # Inicializar bot de trading si está disponible
            if TRADING_BOT_AVAILABLE:
                self._init_trading_bot()
            else:
                logger.warning("⚠️ Bot de trading no disponible - solo API funcionando")
        except Exception as e:
            logger.error(f"❌ Error inicializando TradingBotService: {e}")
            raise

    def _init_health_api(self):
        """Inicializa la API de health check"""
        try:
            if HealthCheckAPI:
                self.health_api = HealthCheckAPI()
                logger.info("🏥 Health Check API inicializada")
            else:
                logger.warning("⚠️ HealthCheckAPI no disponible")
        except Exception as e:
            logger.error(f"❌ Error inicializando Health Check API: {e}")
            raise

    def _init_trading_bot(self):
        """Inicializa el bot de trading"""
        try:
            if not TRADING_BOT_AVAILABLE:
                logger.warning("⚠️ Bot de trading no disponible")
                return
            logger.info("🤖 Inicializando Trading Bot...")
            self.trading_bot = TradingBotMain()
            logger.info("✅ Trading Bot inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando Trading Bot: {e}")
            self.trading_bot = None

    def test_connections(self):
        """Prueba las conexiones del sistema"""
        try:
            logger.info("🔍 Probando conexiones del sistema...")
            success = True

            # Probar Health Check API
            if self.health_api:
                logger.info("✅ Health Check API: OK")
            else:
                logger.error("❌ Health Check API: Error")
                success = False

            # Probar Trading Bot
            if self.trading_bot:
                try:
                    bot_success = self.trading_bot.test_connections()
                    if bot_success:
                        logger.info("✅ Trading Bot: Conexiones OK")
                    else:
                        logger.error("❌ Trading Bot: Error en conexiones")
                        success = False
                except Exception as e:
                    logger.error(f"❌ Trading Bot: Error probando conexiones: {e}")
                    success = False
            else:
                logger.warning("⚠️ Trading Bot: No disponible")

            if success:
                logger.info("✅ Todas las conexiones probadas correctamente")
            else:
                logger.error("❌ Algunas conexiones fallaron")

            return success
        except Exception as e:
            logger.error(f"❌ Error en test_connections: {e}")
            return False

    def get_app(self):
        """Obtiene la aplicación Flask principal"""
        if self.health_api:
            return self.health_api.app
        else:
            # Crear una app básica si no hay health_api
            from flask import Flask
            app = Flask(__name__)
            
            @app.route('/health')
            def health():
                return {"status": "ok", "message": "Servicio funcionando sin bot de trading"}, 200
            
            @app.route('/status')
            def status():
                return {
                    "status": "running",
                    "trading_bot_available": TRADING_BOT_AVAILABLE,
                    "health_api_available": self.health_api is not None
                }, 200
            
            return app

    def run(self):
        """Ejecuta el servicio completo"""
        try:
            logger.info("🚀 Iniciando TradingBotService...")
            
            # Configurar señales para cierre graceful
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)

            # Probar conexiones
            if not self.test_connections():
                logger.warning("⚠️ Continuando con conexiones limitadas")

            # Obtener aplicación Flask
            app = self.get_app()

            # Determinar puerto
            port = int(os.environ.get('PORT', 10000))
            host = '0.0.0.0'

            logger.info(f"🌐 Iniciando servidor en {host}:{port}")
            logger.info(f"🏥 Health Check: http://localhost:{port}/health")
            logger.info(f"📊 Status: http://localhost:{port}/status")

            # Marcar como ejecutándose
            self.is_running = True

            # Ejecutar aplicación
            app.run(host=host, port=port, debug=False)

        except Exception as e:
            logger.error(f"❌ Error ejecutando TradingBotService: {e}")
            raise
        finally:
            self.is_running = False
            logger.info("👋 TradingBotService detenido")

    def _signal_handler(self, signum, frame):
        """Maneja señales de cierre"""
        logger.info(f"🛑 Señal {signum} recibida, cerrando servicio...")
        self.stop()

    def stop(self):
        """Detiene el servicio"""
        try:
            logger.info("🛑 Deteniendo TradingBotService...")
            self.is_running = False
            
            # Detener bot de trading si existe
            if self.trading_bot:
                try:
                    self.trading_bot.stop()
                except Exception as e:
                    logger.error(f"❌ Error deteniendo trading bot: {e}")
            
            logger.info("👋 TradingBotService detenido completamente")
        except Exception as e:
            logger.error(f"❌ Error deteniendo servicio: {e}")

# Instancia global del servicio
service = None

def create_app():
    """Factory function para crear la aplicación"""
    global service
    try:
        if service is None:
            service = TradingBotService()
        return service.get_app()
    except Exception as e:
        logger.error(f"❌ Error creando aplicación: {e}")
        # Fallback a aplicación básica
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/health')
        def health():
            return {"status": "error", "message": str(e)}, 500
        
        return app

# Aplicación principal
app = create_app()

if __name__ == '__main__':
    try:
        service_instance = TradingBotService()
        service_instance.run()
    except KeyboardInterrupt:
        logger.info("🛑 Servicio detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        sys.exit(1)
