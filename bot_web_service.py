"""
Servicio Web principal para Render.com
Usa el health check corregido
"""

import logging
import sys
import os

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

# Configuración de la aplicación
def create_app():
    """Crea y configura la aplicación Flask"""
    try:
        # Crear instancia de HealthCheckAPI
        health_api = HealthCheckAPI()
        app = health_api.app
        
        # Configurar la aplicación con metadatos
        app.config.update({
            'SERVICE_NAME': 'Trading Bot Breakout + Reentry',
            'VERSION': '1.0.0',
            'ENVIRONMENT': 'production'
        })
        
        logger.info("🚀 Aplicación Flask configurada correctamente")
        return app, health_api
        
    except Exception as e:
        logger.error(f"❌ Error creando aplicación: {e}")
        raise

# Crear la aplicación Flask
try:
    app, health_api = create_app()
    logger.info("✅ Servicio web inicializado correctamente")
except Exception as e:
    logger.error(f"❌ Fallo en la inicialización del servicio: {e}")
    sys.exit(1)

if __name__ == '__main__':
    # Para desarrollo local
    try:
        logger.info("🔧 Iniciando en modo desarrollo...")
        health_api.run(debug=True)
    except Exception as e:
        logger.error(f"❌ Error ejecutando en modo desarrollo: {e}")
        sys.exit(1)
