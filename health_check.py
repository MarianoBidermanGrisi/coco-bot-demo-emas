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

@self.app.route('/config', methods=['GET'])
def config():
"""Endpoint de configuración"""
try:
return self.jsonify(self.get_configuration())
except Exception as e:
logger.error(f"❌ Error obteniendo configuración: {e}")
return self.jsonify({
'error': str(e),
'timestamp': datetime.now().isoformat()
}), 500

@self.app.route('/', methods=['GET'])
def index():
"""Página principal"""
return self.jsonify({
'service': 'Trading Bot Breakout + Reentry',
'version': '2.0.0',
'status': 'running',
'timestamp': datetime.now().isoformat(),
'trading_bot': {
'available': self.trading_bot_status['available'],
'running': self.trading_bot_status['running']
},
'endpoints': {
'health': '/health',
'status': '/status',
'trading_bot': '/trading-bot',
'ready': '/ready',
'metrics': '/metrics',
'config': '/config'
}
})

def get_health_status(self) -> Dict[str, Any]:
"""Obtiene el estado de salud del servicio"""
try:
# Verificar componentes críticos
checks = {
'api': self.check_api_health(),
'config': self.check_configuration(),
'database': self.check_database_connection(),
'trading_bot': self.check_trading_bot_health()
}

# Determinar estado general
all_healthy = all(check['status'] == 'healthy' for check in checks.values())
status = {
'status': 'healthy' if all_healthy else 'degraded',
'timestamp': datetime.now().isoformat(),
'uptime_seconds': int(time.time() - self.start_time),
'checks': checks,
'version': '2.0.0'
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
'memory_usage': 'N/A', # Se podría agregar psutil
'disk_usage': 'N/A',
'cpu_usage': 'N/A'
},
'config_summary': {
'service': 'active',
'environment': 'production',
'trading_bot_available': self.trading_bot_status['available']
},
'trading_bot': self.get_trading_bot_status()
}
return detailed_status
except Exception as e:
logger.error(f"❌ Error obteniendo estado detallado: {e}")
return {
'status': 'error',
'error': str(e),
'timestamp': datetime.now().isoformat()
}

def get_trading_bot_status(self) -> Dict[str, Any]:
"""Obtiene el estado específico del bot de trading"""
try:
status = {
'available': self.trading_bot_status['available'],
'running': self.trading_bot_status['running'],
'last_update': self.trading_bot_status['last_update'],
'error': self.trading_bot_status['error'],
'timestamp': datetime.now().isoformat()
}

# Verificar si hay archivos de estado del bot
status_files = self._check_status_files()
status['status_files'] = status_files

return status
except Exception as e:
logger.error(f"❌ Error obteniendo estado del trading bot: {e}")
return {
'available': False,
'running': False,
'error': str(e),
'timestamp': datetime.now().isoformat()
}

def _check_status_files(self) -> Dict[str, Any]:
"""Verifica la existencia de archivos de estado del bot"""
try:
files_status = {}

# Verificar archivos comunes del bot
possible_files = [
'data/estado_bot_v23.json',
'data/operaciones_log_v23.csv',
'data/mejores_parametros.json',
'logs/trading_bot.log'
]

for file_path in possible_files:
if os.path.exists(file_path):
stat = os.stat(file_path)
files_status[file_path] = {
'exists': True,
'size': stat.st_size,
'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
}
else:
files_status[file_path] = {'exists': False}

return files_status
except Exception as e:
logger.error(f"❌ Error verificando archivos de estado: {e}")
return {}

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

def check_trading_bot_health(self) -> Dict[str, Any]:
"""Verifica la salud del bot de trading"""
try:
if not self.trading_bot_status['available']:
return {
'status': 'degraded',
'message': 'Bot de trading no disponible'
}

if self.trading_bot_status['running']:
return {
'status': 'healthy',
'message': 'Bot de trading ejecutándose correctamente'
}
else:
return {
'status': 'degraded',
'message': 'Bot de trading no está ejecutándose'
}
except Exception as e:
return {
'status': 'error',
'message': f'Error verificando bot de trading: {e}'
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
'environment': 'production',
'trading_bot_available': self.trading_bot_status['available']
},
'trading_bot_metrics': self._get_trading_bot_metrics()
}
except Exception as e:
logger.error(f"❌ Error obteniendo métricas: {e}")
return {
'error': str(e),
'timestamp': datetime.now().isoformat()
}

def _get_trading_bot_metrics(self) -> Dict[str, Any]:
"""Obtiene métricas específicas del bot de trading"""
try:
metrics = {
'available': self.trading_bot_status['available'],
'running': self.trading_bot_status['running'],
'last_update': self.trading_bot_status['last_update']
}

# Verificar archivos de datos para estadísticas
if os.path.exists('data/operaciones_log_v23.csv'):
try:
import pandas as pd
df = pd.read_csv('data/operaciones_log_v23.csv')
metrics['total_operations'] = len(df)
if 'profit' in df.columns:
metrics['total_profit'] = float(df['profit'].sum()) if not df['profit'].empty else 0
except Exception:
metrics['total_operations'] = 'N/A'

return metrics
except Exception as e:
logger.error(f"❌ Error obteniendo métricas del trading bot: {e}")
return {}

def get_configuration(self) -> Dict[str, Any]:
"""Obtiene la configuración del servicio"""
try:
return {
'timestamp': datetime.now().isoformat(),
'service': {
'name': 'Trading Bot Breakout + Reentry',
'version': '2.0.0',
'environment': 'production'
},
'components': {
'health_check_api': {
'available': True,
'running': True
},
'trading_bot': {
'available': self.trading_bot_status['available'],
'running': self.trading_bot_status['running']
}
},
'environment_variables': {
var: self._get_env_var(var) for var in ['PORT', 'BINANCE_API_KEY', 'BINANCE_SECRET_KEY'] 
if self._get_env_var(var)
}
}
except Exception as e:
logger.error(f"❌ Error obteniendo configuración: {e}")
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
logger.info(f"🤖 Trading Bot status en: http://{host}:{port}/trading-bot")
logger.info(f"🔍 Readiness check en: http://{host}:{port}/ready")
logger.info(f"📊 Métricas en: http://{host}:{port}/metrics")
logger.info(f"⚙️ Configuración en: http://{host}:{port}/config")
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
