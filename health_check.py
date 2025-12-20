"""
Health Check API para Render.com
Maneja endpoints de salud del servicio y estado del bot de trading
"""
import logging
import time
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthCheckAPI:
    """API de Health Check para Render.com con información del bot de trading"""
    def __init__(self):
        """Inicializa la API de health check"""
        try:
            self.app = self._create_flask_app()
            self.start_time = time.time()
            self.setup_routes()
            # Estado del bot de trading
            self.trading_bot_status = {
                'available': False,
                'running': False,
                'last_update': None,
                'error': None
            }
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

    def update_trading_bot_status(self, status: Dict[str, Any]):
        """Actualiza el estado del bot de trading"""
        try:
            self.trading_bot_status.update({
                'available': status.get('available', False),
                'running': status.get('running', False),
                'last_update': datetime.now().isoformat(),
                'error': status.get('error')
            })
            logger.debug(f"🔄 Estado del trading bot actualizado: {self.trading_bot_status}")
        except Exception as e:
            logger.error(f"❌ Error actualizando estado del trading bot: {e}")

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

        @self.app.route('/trading-bot', methods=['GET'])
        def trading_bot_status():
            """Endpoint específico para el estado del bot de trading"""
            try:
                return self.jsonify(self.get_trading_bot_status())
            except Exception as e:
                logger.error(f"❌ Error obteniendo estado del trading bot: {e}")
                return self.jsonify({
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

        @self.app.route('/info', methods=['GET'])
        def info():
            """Información del sistema"""
            try:
                return self.jsonify(self.get_system_info())
            except Exception as e:
                logger.error(f"❌ Error obteniendo info del sistema: {e}")
                return self.jsonify({
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500

    def get_health_status(self) -> Dict[str, Any]:
        """Obtiene el estado general de salud"""
        try:
            uptime = time.time() - self.start_time
            
            # Verificar componentes básicos
            components = {
                'api': True,
                'flask': True,
                'trading_bot': self.trading_bot_status.get('available', False)
            }
            
            # Determinar estado general
            all_healthy = all(components.values())
            
            return {
                'status': 'healthy' if all_healthy else 'degraded',
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': round(uptime, 2),
                'components': components,
                'version': '1.0.0'
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo health status: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_detailed_status(self) -> Dict[str, Any]:
        """Obtiene estado detallado del sistema"""
        try:
            uptime = time.time() - self.start_time
            
            return {
                'status': 'running',
                'timestamp': datetime.now().isoformat(),
                'uptime': {
                    'seconds': round(uptime, 2),
                    'formatted': self._format_uptime(uptime)
                },
                'service': {
                    'name': 'Trading Bot Demo EMAS',
                    'version': '1.0.0',
                    'environment': os.environ.get('ENVIRONMENT', 'production')
                },
                'trading_bot': self.trading_bot_status,
                'system': self.get_system_info(),
                'endpoints': {
                    'health': '/health',
                    'status': '/status',
                    'trading_bot': '/trading-bot',
                    'ready': '/ready',
                    'metrics': '/metrics',
                    'info': '/info'
                }
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo status detallado: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_trading_bot_status(self) -> Dict[str, Any]:
        """Obtiene estado específico del bot de trading"""
        try:
            return {
                'trading_bot': self.trading_bot_status,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo status del trading bot: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def is_ready(self) -> bool:
        """Verifica si el servicio está listo para recibir tráfico"""
        try:
            # Verificar que Flask esté funcionando
            if not hasattr(self, 'app') or self.app is None:
                return False
            
            # Verificar uptime mínimo (al menos 5 segundos)
            uptime = time.time() - self.start_time
            if uptime < 5:
                return False
            
            return True
        except Exception as e:
            logger.error(f"❌ Error en readiness check: {e}")
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del sistema"""
        try:
            import psutil
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': {
                    'percent': psutil.virtual_memory().percent,
                    'available': psutil.virtual_memory().available,
                    'total': psutil.virtual_memory().total
                },
                'disk': {
                    'percent': psutil.disk_usage('/').percent,
                    'free': psutil.disk_usage('/').free,
                    'total': psutil.disk_usage('/').total
                },
                'processes': len(psutil.pids())
            }
        except ImportError:
            logger.warning("⚠️ psutil no disponible, métricas limitadas")
            return {
                'timestamp': datetime.now().isoformat(),
                'note': 'psutil no disponible'
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo métricas: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_system_info(self) -> Dict[str, Any]:
        """Obtiene información del sistema"""
        try:
            return {
                'platform': sys.platform,
                'python_version': sys.version,
                'working_directory': os.getcwd(),
                'environment_variables': {
                    'PORT': os.environ.get('PORT'),
                    'ENVIRONMENT': os.environ.get('ENVIRONMENT'),
                    'RENDER': os.environ.get('RENDER', 'false')
                }
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo info del sistema: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _format_uptime(self, uptime_seconds: float) -> str:
        """Formatea el uptime en formato legible"""
        try:
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            seconds = int(uptime_seconds % 60)
            
            parts = []
            if days > 0:
                parts.append(f"{days}d")
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")
            if seconds > 0 or not parts:
                parts.append(f"{seconds}s")
            
            return " ".join(parts)
        except Exception:
            return f"{uptime_seconds:.2f}s"

# Instancia global de la API
health_api = None

def get_health_check_api():
    """Obtiene la instancia global de HealthCheckAPI"""
    global health_api
    if health_api is None:
        health_api = HealthCheckAPI()
    return health_api

if __name__ == '__main__':
    # Script de prueba
    print("🧪 Probando HealthCheckAPI...")
    
    try:
        api = HealthCheckAPI()
        print("✅ HealthCheckAPI creada correctamente")
        print(f"🏥 Health: http://localhost:5000/health")
        print(f"📊 Status: http://localhost:5000/status")
        print(f"🤖 Trading Bot: http://localhost:5000/trading-bot")
        print(f"📈 Metrics: http://localhost:5000/metrics")
        print(f"ℹ️ Info: http://localhost:5000/info")
        print(f"✅ Ready: http://localhost:5000/ready")
        
        # Ejecutar en modo desarrollo
        print("\n🚀 Iniciando servidor de desarrollo...")
        api.app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
