"""
Health Check API para Render.com
Maneja endpoints de salud del servicio para Render
"""

import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthCheckAPI:
    """API de Health Check para Render.com"""
    
    def __init__(self):
        """Inicializa la API de health check"""
        try:
            self.app = self._create_flask_app()
            self.start_time = time.time()
            self.setup_routes()
            logger.info("🏥 HealthCheckAPI inicializada correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando HealthCheckAPI: {e}")
            raise
    
    def _create_flask_app(self):
        """Crea la instancia de Flask"""
        try:
            from flask import Flask, jsonify
            # Hacer jsonify disponible para toda la clase
            self.jsonify = jsonify
            return Flask(__name__)
        except ImportError as e:
            logger.error(f"❌ Error importando Flask: {e}")
            raise ImportError("Flask no está disponible. Instala con: pip install flask")
    
    def setup_routes(self):
        """Configura las rutas de la API"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Endpoint principal de health check"""
            try:
                health_status = self.get_health_status()
                status_code = 200 if health_status['status'] == 'healthy' else 503
                return self.jsonify(health_status), status_code
            except Exception as e:
                logger.error(f"❌ Error en health check: {e}")
                return self.jsonify({
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500

        @self.app.route('/status', methods=['GET'])
        def status():
            """Endpoint de estado detallado"""
            try:
                return self.jsonify(self.get_detailed_status())
            except Exception as e:
                logger.error(f"❌ Error en status detallado: {e}")
                return self.jsonify({
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500

        @self.app.route('/ready', methods=['GET'])
        def readiness_check():
            """Check de readiness para Kubernetes/Render"""
            try:
                ready = self.is_ready()
                status_code = 200 if ready else 503
                return self.jsonify({
                    'ready': ready,
                    'timestamp': datetime.now().isoformat()
                }), status_code
            except Exception as e:
                logger.error(f"❌ Error en readiness check: {e}")
                return self.jsonify({
                    'ready': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500

        @self.app.route('/metrics', methods=['GET'])
        def metrics():
            """Endpoint de métricas"""
            try:
                return self.jsonify(self.get_metrics())
            except Exception as e:
                logger.error(f"❌ Error obteniendo métricas: {e}")
                return self.jsonify({
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500

        @self.app.route('/', methods=['GET'])
        def index():
            """Página principal"""
            return self.jsonify({
                'service': 'Trading Bot Breakout + Reentry',
                'version': '1.0.0',
                'status': 'running',
                'timestamp': datetime.now().isoformat(),
                'endpoints': {
                    'health': '/health',
                    'status': '/status',
                    'ready': '/ready',
                    'metrics': '/metrics'
                }
            })

    def get_health_status(self) -> Dict[str, Any]:
        """Obtiene el estado de salud del servicio"""
        try:
            # Verificar componentes críticos
            checks = {
                'api': self.check_api_health(),
                'config': self.check_configuration(),
                'database': self.check_database_connection()
            }

            # Determinar estado general
            all_healthy = all(check['status'] == 'healthy' for check in checks.values())

            status = {
                'status': 'healthy' if all_healthy else 'degraded',
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': int(time.time() - self.start_time),
                'checks': checks,
                'version': '1.0.0'
            }

            return status

        except Exception as e:
            logger.error(f"❌ Error obteniendo estado de salud: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_detailed_status(self) -> Dict[str, Any]:
        """Obtiene estado detallado del servicio"""
        try:
            base_status = self.get_health_status()

            # Información adicional
            detailed_status = {
                **base_status,
                'environment': {
                    'platform': 'Render.com',
                    'python_version': '3.x',
                    'uptime_hours': round((time.time() - self.start_time) / 3600, 2)
                },
                'system': {
                    'memory_usage': 'N/A',  # Se podría agregar psutil
                    'disk_usage': 'N/A',
                    'cpu_usage': 'N/A'
                },
                'config_summary': {
                    'service': 'active',
                    'environment': 'production'
                }
            }

            return detailed_status

        except Exception as e:
            logger.error(f"❌ Error obteniendo estado detallado: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def check_api_health(self) -> Dict[str, Any]:
        """Verifica la salud de la API"""
        try:
            return {
                'status': 'healthy',
                'message': 'API respondiendo correctamente',
                'response_time_ms': 0
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error verificando API: {e}'
            }

    def check_configuration(self) -> Dict[str, Any]:
        """Verifica la configuración"""
        try:
            # Verificar variables de entorno básicas
            required_vars = ['PORT']
            missing_vars = []
            
            for var in required_vars:
                if not self._get_env_var(var):
                    missing_vars.append(var)
            
            if missing_vars:
                return {
                    'status': 'degraded',
                    'message': f'Variables faltantes: {", ".join(missing_vars)}'
                }
            else:
                return {
                    'status': 'healthy',
                    'message': 'Configuración básica correcta'
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error verificando configuración: {e}'
            }

    def check_database_connection(self) -> Dict[str, Any]:
        """Verifica la conexión a base de datos (simulado)"""
        try:
            # Simular verificación de base de datos
            # En un caso real, aquí verificarías la conexión real
            return {
                'status': 'healthy',
                'message': 'Base de datos disponible (simulado)'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error verificando base de datos: {e}'
            }

    def is_ready(self) -> bool:
        """Verifica si el servicio está listo para recibir tráfico"""
        try:
            # Verificaciones críticas para readiness
            health = self.get_health_status()
            
            # Debe tener al menos la API y configuración funcionando
            api_healthy = health['checks'].get('api', {}).get('status') == 'healthy'
            config_healthy = health['checks'].get('config', {}).get('status') in ['healthy', 'degraded']
            
            return api_healthy and config_healthy

        except Exception as e:
            logger.error(f"❌ Error en readiness check: {e}")
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del servicio"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': int(time.time() - self.start_time),
                'uptime_hours': round((time.time() - self.start_time) / 3600, 2),
                'api_stats': {
                    'requests_handled': 0,
                    'average_response_time': 0
                },
                'config_status': {
                    'configured': True,
                    'environment': 'production'
                }
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo métricas: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _get_env_var(self, var_name: str) -> Optional[str]:
        """Obtiene variable de entorno"""
        try:
            import os
            return os.environ.get(var_name)
        except Exception:
            return None

    def run(self, host='0.0.0.0', port=None, debug=False):
        """Ejecuta la API"""
        try:
            # Obtener puerto de variable de entorno o usar por defecto
            if port is None:
                port = int(self._get_env_var('PORT') or 5000)
            
            logger.info(f"🚀 Iniciando HealthCheckAPI en {host}:{port}")
            logger.info(f"📊 Health check disponible en: http://{host}:{port}/health")
            logger.info(f"📈 Status detallado en: http://{host}:{port}/status")
            logger.info(f"🔍 Readiness check en: http://{host}:{port}/ready")
            logger.info(f"📊 Métricas en: http://{host}:{port}/metrics")

            self.app.run(host=host, port=port, debug=debug)

        except Exception as e:
            logger.error(f"❌ Error ejecutando HealthCheckAPI: {e}")
            raise

# Funciones de utilidad para facilitar la importación
def create_health_check_app():
    """Crea una instancia de la API de health check"""
    return HealthCheckAPI()

def get_health_check_api():
    """Obtiene una instancia de la API de health check"""
    return create_health_check_app()

# Para compatibilidad con imports existentes
health_check_api = HealthCheckAPI()

if __name__ == '__main__':
    # Ejecutar como script independiente
    try:
        api = HealthCheckAPI()
        port = int(api._get_env_var('PORT') or 5000)
        api.run(port=port, debug=True)
    except Exception as e:
        logger.error(f"❌ Error ejecutando script: {e}")
