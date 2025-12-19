"""
Servicio Web principal para Render.com
Usa el health check corregido
"""

import logging
from health_check import HealthCheckAPI

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear la aplicación Flask
app = HealthCheckAPI().app

if __name__ == '__main__':
    # Para desarrollo local
    health_api = HealthCheckAPI()
    health_api.run(debug=True)
