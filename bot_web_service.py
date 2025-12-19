#!/usr/bin/env python3
"""
Archivo de entrada para Gunicorn
Conecta la aplicación Flask con el servidor web
"""

import os
import sys

# Agregar el directorio src al path para importaciones
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Variables para almacenar errores
import_error = None

try:
# Importar la aplicación Flask desde el módulo de health check
from api.health_check import health_check_api

# Crear la instancia de aplicación Flask para Gunicorn
app = health_check_api.app

print("✅ Aplicación Flask cargada correctamente desde api.health_check")

except ImportError as e:
import_error = str(e)
print(f"❌ Error importando aplicación: {e}")
print("Intentando importar desde ubicación alternativa...")

try:
# Intentar importar directamente la clase
from src.api.health_check import HealthCheckAPI

# Crear instancia y obtener la app
health_api = HealthCheckAPI()
app = health_api.app

print("✅ Aplicación Flask cargada usando importación directa")

except ImportError as e2:
import_error = str(e2)
print(f"❌ Error crítico: {e2}")
print("Creando aplicación Flask básica de emergencia...")

from flask import Flask

# Crear aplicación Flask básica como fallback
app = Flask(__name__)

@app.route('/')
def emergency_home():
return {
'status': 'emergency_mode',
'message': 'La aplicación principal no pudo cargarse',
'error': import_error or 'Unknown import error',
'timestamp': '2025-12-20T02:46:44Z'
}

@app.route('/health')
def emergency_health():
return {
'status': 'emergency',
'health': 'degraded',
'error': import_error or 'Unknown import error',
'timestamp': '2025-12-20T02:46:44Z'
}

print("⚠️ Aplicación Flask de emergencia creada")

if __name__ == "__main__":
# Ejecutar la aplicación directamente si se ejecuta como script
try:
if 'health_check_api' in locals():
health_check_api.run()
else:
# Ejecutar la app Flask básica
app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False)
except Exception as e:
print(f"❌ Error ejecutando aplicación: {e}")
sys.exit(1)
