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
raise

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
self.health_api = HealthCheckAPI()
logger.info("🏥 Health Check API inicializada")
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
logger.error(f"❌ Error probando conexiones: {e}")
return False

def run_health_api(self):
"""Ejecuta la API de health check"""
try:
logger.info("🏥 Iniciando Health Check API...")
port = int(os.environ.get('PORT', 5000))
self.health_api.run(host='0.0.0.0', port=port, debug=False)
except Exception as e:
logger.error(f"❌ Error en Health Check API: {e}")

def run_trading_bot(self):
"""Ejecuta el bot de trading"""
try:
if not self.trading_bot:
logger.warning("⚠️ Trading Bot no disponible")
return

logger.info("🤖 Iniciando Trading Bot...")
self.trading_bot.start()
except Exception as e:
logger.error(f"❌ Error en Trading Bot: {e}")

def start(self):
"""Inicia el servicio completo"""
try:
logger.info("=" * 70)
logger.info("🤖 BOT DE TRADING - BREAKOUT + REENTRY")
logger.info("🚀 Servicio Web + Bot de Trading")
logger.info("=" * 70)

# Probar conexiones
if not self.test_connections():
logger.error("❌ Error en conexiones, continuando con servicios disponibles...")

self.is_running = True

# Iniciar Health Check API en hilo separado
if self.health_api:
api_thread = threading.Thread(target=self.run_health_api, daemon=True)
api_thread.start()
self.threads.append(api_thread)
logger.info("✅ Health Check API iniciada en hilo separado")

# Dar tiempo a la API para inicializar
time.sleep(2)

# Iniciar Trading Bot en hilo separado (si está disponible)
if self.trading_bot:
trading_thread = threading.Thread(target=self.run_trading_bot, daemon=True)
trading_thread.start()
self.threads.append(trading_thread)
logger.info("✅ Trading Bot iniciado en hilo separado")
else:
logger.warning("⚠️ Trading Bot no iniciado (no disponible)")

logger.info("✅ Servicio completo iniciado correctamente")
logger.info("📊 Health Check: Disponible")
if self.trading_bot:
logger.info("🤖 Trading Bot: Activo")
else:
logger.info("🤖 Trading Bot: Inactivo")

# Mantener el servicio corriendo
self._keep_alive()

except KeyboardInterrupt:
logger.info("🛑 Deteniendo servicio por solicitud del usuario")
self.stop()
except Exception as e:
logger.error(f"❌ Error en start: {e}")
self.stop()

def _keep_alive(self):
"""Mantiene el servicio corriendo y maneja señales"""
try:
def signal_handler(signum, frame):
logger.info(f"🛑 Señal {signum} recibida, deteniendo servicio...")
self.stop()
sys.exit(0)

# Configurar manejo de señales
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Mantener el hilo principal activo
while self.is_running:
time.sleep(1)

except Exception as e:
logger.error(f"❌ Error en keep_alive: {e}")

def stop(self):
"""Detiene el servicio"""
try:
logger.info("🛑 Deteniendo servicio...")
self.is_running = False

# Detener Trading Bot
if hasattr(self, 'trading_bot') and self.trading_bot:
try:
self.trading_bot.stop()
logger.info("✅ Trading Bot detenido")
except Exception as e:
logger.error(f"❌ Error deteniendo Trading Bot: {e}")

# Esperar a que terminen los hilos
for thread in self.threads:
if thread.is_alive():
logger.info("⏳ Esperando que terminen los hilos...")
thread.join(timeout=5)

logger.info("👋 Servicio detenido completamente")
except Exception as e:
logger.error(f"❌ Error deteniendo servicio: {e}")

# Configuración de la aplicación Flask
def create_app():
"""Crea y configura la aplicación Flask"""
try:
# Crear instancia del servicio completo
service = TradingBotService()
app = service.health_api.app if service.health_api else None

if not app:
raise Exception("No se pudo crear la aplicación Flask")

# Configurar la aplicación con metadatos
app.config.update({
'SERVICE_NAME': 'Trading Bot Breakout + Reentry',
'VERSION': '2.0.0',
'ENVIRONMENT': 'production',
'TRADING_BOT_AVAILABLE': TRADING_BOT_AVAILABLE
})

# Agregar información del servicio a la app
app.service = service

logger.info("🚀 Aplicación Flask configurada correctamente")
return app, service
except Exception as e:
logger.error(f"❌ Error creando aplicación: {e}")
raise

# Crear la aplicación Flask
try:
app, service = create_app()
logger.info("✅ Servicio web inicializado correctamente")
except Exception as e:
logger.error(f"❌ Fallo en la inicialización del servicio: {e}")
sys.exit(1)

if __name__ == '__main__':
# Para desarrollo local
try:
logger.info("🔧 Iniciando en modo desarrollo...")
service.start()
except Exception as e:
logger.error(f"❌ Error ejecutando en modo desarrollo: {e}")
sys.exit(1)

