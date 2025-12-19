"""
Health Check API para Render.com
Maneja endpoints de salud del servicio para Render
"""

import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, jsonify, request

from ..config.settings import *
from ..config.environment import get_env_manager
from ..apiBinance.binance_client import get_binance_client

logger = logging.getLogger(__name__)

class HealthCheckAPI:
"""API de Health Check para Render.com"""

def __init__(self):
"""Inicializa la API de health check"""
self.app = Flask(__name__)
self.env_manager = get_env_manager()
self.binance_client = get_binance_client()
self.start_time = time.time()
self.setup_routes()

logger.info("🏥 HealthCheckAPI inicializada")

def setup_routes(self):
"""Configura las rutas de la API"""

@self.app.route(HEALTH_CHECK_PATH, methods=['GET'])
def health_check():
"""Endpoint principal de health check"""
try:
health_status = self.get_health_status()
status_code = 200 if health_status['status'] == 'healthy' else 503
return jsonify(health_status), status_code
except Exception as e:
logger.error(f"❌ Error en health check: {e}")
return jsonify({
'status': 'error',
'error': str(e),
'timestamp': datetime.now().isoformat()
}), 500

@self.app.route('/status', methods=['GET'])
def status():
"""Endpoint de estado detallado"""
try:
return jsonify(self.get_detailed_status())
except Exception as e:
logger.error(f"❌ Error en status detallado: {e}")
return jsonify({
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
return jsonify({
'ready': ready,
'timestamp': datetime.now().isoformat()
}), status_code
except Exception as e:
logger.error(f"❌ Error en readiness check: {e}")
return jsonify({
'ready': False,
'error': str(e),
'timestamp': datetime.now().isoformat()
}), 500

@self.app.route('/metrics', methods=['GET'])
def metrics():
"""Endpoint de métricas"""
try:
return jsonify(self.get_metrics())
except Exception as e:
logger.error(f"❌ Error obteniendo métricas: {e}")
return jsonify({
'error': str(e),
'timestamp': datetime.now().isoformat()
}), 500

@self.app.route('/', methods=['GET'])
def index():
"""Página principal"""
return jsonify({
'service': 'Trading Bot Breakout + Reentry',
'version': '1.0.0',
'status': 'running',
'timestamp': datetime.now().isoformat(),
'endpoints': {
'health': HEALTH_CHECK_PATH,
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
'config': self.check_configuration(),
'binance_api': self.check_binance_connection(),
'telegram': self.check_telegram_config()
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
'render_external_url': self.env_manager._render_external_url,
'webhook_url': self.env_manager.get_webhook_url(),
'telegram_enabled': self.env_manager.is_telegram_enabled()
},
'system': {
'python_version': '3.x',
'platform': 'Render.com',
'memory_usage': 'N/A',  # Se podría agregar psutil
'disk_usage': 'N/A'
},
'binance': self.binance_client.get_connection_stats(),
'config_summary': {
'symbols_count': len(self.env_manager.get_trading_config().get('symbols', [])),
'auto_optimize': self.env_manager.get_trading_config().get('auto_optimize', False),
'scan_interval': self.env_manager.get_trading_config().get('scan_interval_minutes', 1)
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

def check_configuration(self) -> Dict[str, Any]:
"""Verifica la configuración"""
try:
if self.env_manager.is_configured():
return {
'status': 'healthy',
'message': 'Configuración cargada correctamente'
}
else:
return {
'status': 'unhealthy',
'message': 'Configuración incompleta'
}
except Exception as e:
return {
'status': 'error',
'message': f'Error verificando configuración: {e}'
}

def check_binance_connection(self) -> Dict[str, Any]:
"""Verifica la conexión con Binance"""
try:
if self.binance_client.test_connection():
stats = self.binance_client.get_connection_stats()
return {
'status': 'healthy',
'message': 'Conexión con Binance exitosa',
'details': stats
}
else:
return {
'status': 'unhealthy',
'message': 'No se pudo conectar con Binance'
}
except Exception as e:
return {
'status': 'error',
'message': f'Error verificando Binance: {e}'
}

def check_telegram_config(self) -> Dict[str, Any]:
"""Verifica la configuración de Telegram"""
try:
telegram_config = self.env_manager.get_telegram_config()
if telegram_config['token'] and telegram_config['chat_ids']:
return {
'status': 'healthy',
'message': 'Telegram configurado correctamente',
'chat_ids_count': len(telegram_config['chat_ids'])
}
else:
return {
'status': 'degraded',
'message': 'Telegram no configurado (opcional)'
}
except Exception as e:
return {
'status': 'error',
'message': f'Error verificando Telegram: {e}'
}

def is_ready(self) -> bool:
"""Verifica si el servicio está listo para recibir tráfico"""
try:
# Verificaciones críticas para readiness
if not self.env_manager.is_configured():
return False

if not self.binance_client.test_connection():
return False

return True

except Exception as e:
logger.error(f"❌ Error en readiness check: {e}")
return False

def get_metrics(self) -> Dict[str, Any]:
"""Obtiene métricas del servicio"""
try:
return {
'timestamp': datetime.now().isoformat(),
'uptime_seconds': int(time.time() - self.start_time),
'binance_stats': self.binance_client.get_connection_stats(),
'config_status': {
'configured': self.env_manager.is_configured(),
'telegram_enabled': self.env_manager.is_telegram_enabled()
}
}
except Exception as e:
logger.error(f"❌ Error obteniendo métricas: {e}")
return {
'error': str(e),
'timestamp': datetime.now().isoformat()
}

def run(self, host='0.0.0.0', port=DEFAULT_PORT, debug=False):
"""Ejecuta la API"""
try:
logger.info(f"🚀 Iniciando HealthCheckAPI en {host}:{port}")
logger.info(f"📊 Health check disponible en: http://{host}:{port}{HEALTH_CHECK_PATH}")
logger.info(f"📈 Status detallado en: http://{host}:{port}/status")
logger.info(f"🔍 Readiness check en: http://{host}:{port}/ready")

self.app.run(host=host, port=port, debug=debug)

except Exception as e:
logger.error(f"❌ Error ejecutando HealthCheckAPI: {e}")
raise

# Instancia global de la API
health_check_api = HealthCheckAPI()

def get_health_check_api() -> HealthCheckAPI:
"""Obtiene la instancia global de la API de health check"""
return health_check_api

