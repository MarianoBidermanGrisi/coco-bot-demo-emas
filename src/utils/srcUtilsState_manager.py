"""
Gestor de Estado del Bot
**REGLA DE ORO: NO MODIFICAR LA LÓGICA ORIGINAL**
Código copiado íntegramente del archivo original
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from ..config.settings import ESTADO_BOT_FILE

logger = logging.getLogger(__name__)

class StateManager:
    """
    Gestor de Estado - LÓGICA ORIGINAL INTACTA
    NO MODIFICAR ESTE CÓDIGO
    """
    
    def __init__(self, estado_file: str = None):
        """Inicializa el gestor de estado"""
        self.estado_file = estado_file or ESTADO_BOT_FILE
        self.estado_cache = {}
        logger.info(f"💾 StateManager inicializado - Archivo: {self.estado_file}")
    
    def cargar_estado(self) -> Dict[str, Any]:
        """Carga el estado del bot - LÓGICA ORIGINAL INTACTA"""
        try:
            if os.path.exists(self.estado_file):
                with open(self.estado_file, 'r', encoding='utf-8') as f:
                    estado = json.load(f)
                
                # Convertir fechas de string a datetime
                if 'ultima_optimizacion' in estado:
                    estado['ultima_optimizacion'] = datetime.fromisoformat(estado['ultima_optimizacion'])
                if 'ultima_busqueda_config' in estado:
                    for simbolo, fecha_str in estado['ultima_busqueda_config'].items():
                        estado['ultima_busqueda_config'][simbolo] = datetime.fromisoformat(fecha_str)
                if 'breakout_history' in estado:
                    for simbolo, fecha_str in estado['breakout_history'].items():
                        estado['breakout_history'][simbolo] = datetime.fromisoformat(fecha_str)
                
                # Cargar breakouts y reingresos esperados
                if 'esperando_reentry' in estado:
                    for simbolo, info in estado['esperando_reentry'].items():
                        info['timestamp'] = datetime.fromisoformat(info['timestamp'])
                        estado['esperando_reentry'][simbolo] = info
                
                if 'breakouts_detectados' in estado:
                    for simbolo, info in estado['breakouts_detectados'].items():
                        info['timestamp'] = datetime.fromisoformat(info['timestamp'])
                        estado['breakouts_detectados'][simbolo] = info
                
                self.estado_cache = estado
                logger.info("✅ Estado cargado correctamente desde archivo")
                return estado
            else:
                logger.info("ℹ️ No existe archivo de estado, iniciando con estado limpio")
                return self._crear_estado_inicial()
                
        except Exception as e:
            logger.error(f"❌ Error cargando estado: {e}")
            return self._crear_estado_inicial()
    
    def guardar_estado(self, estado: Dict[str, Any]) -> bool:
        """Guarda el estado del bot - LÓGICA ORIGINAL INTACTA"""
        try:
            # Crear copia del estado para serializar
            estado_serializable = estado.copy()
            
            # Convertir datetime a string para serialización JSON
            if 'ultima_optimizacion' in estado_serializable:
                estado_serializable['ultima_optimizacion'] = estado['ultima_optimizacion'].isoformat()
            
            if 'ultima_busqueda_config' in estado_serializable:
                estado_serializable['ultima_busqueda_config'] = {
                    k: v.isoformat() for k, v in estado['ultima_busqueda_config'].items()
                }
            
            if 'breakout_history' in estado_serializable:
                estado_serializable['breakout_history'] = {
                    k: v.isoformat() for k, v in estado['breakout_history'].items()
                }
            
            if 'esperando_reentry' in estado_serializable:
                estado_serializable['esperando_reentry'] = {
                    k: {
                        'tipo': v['tipo'],
                        'timestamp': v['timestamp'].isoformat(),
                        'precio_breakout': v['precio_breakout'],
                        'config': v.get('config', {})
                    } for k, v in estado['esperando_reentry'].items()
                }
            
            if 'breakouts_detectados' in estado_serializable:
                estado_serializable['breakouts_detectados'] = {
                    k: {
                        'tipo': v['tipo'],
                        'timestamp': v['timestamp'].isoformat(),
                        'precio_breakout': v.get('precio_breakout', 0)
                    } for k, v in estado['breakouts_detectados'].items()
                }
            
            estado_serializable['timestamp_guardado'] = datetime.now().isoformat()
            
            # Guardar archivo
            with open(self.estado_file, 'w', encoding='utf-8') as f:
                json.dump(estado_serializable, f, indent=2, ensure_ascii=False)
            
            # Actualizar cache
            self.estado_cache = estado.copy()
            
            logger.info("💾 Estado guardado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando estado: {e}")
            return False
    
    def _crear_estado_inicial(self) -> Dict[str, Any]:
        """Crea estado inicial - LÓGICA ORIGINAL INTACTA"""
        estado_inicial = {
            'ultima_optimizacion': datetime.now(),
            'operaciones_desde_optimizacion': 0,
            'total_operaciones': 0,
            'breakout_history': {},
            'config_optima_por_simbolo': {},
            'ultima_busqueda_config': {},
            'operaciones_activas': {},
            'senales_enviadas': [],
            'esperando_reentry': {},
            'breakouts_detectados': {},
            'timestamp_creado': datetime.now().isoformat()
        }
        
        self.estado_cache = estado_inicial
        return estado_inicial
    
    def get_estado_cache(self) -> Dict[str, Any]:
        """Obtiene el estado en cache"""
        return self.estado_cache.copy()
    
    def update_estado_cache(self, key: str, value: Any):
        """Actualiza una clave específica del cache"""
        try:
            self.estado_cache[key] = value
            logger.debug(f"🔄 Cache actualizado: {key}")
        except Exception as e:
            logger.error(f"❌ Error actualizando cache {key}: {e}")
    
    def limpiar_estado_antiguo(self, dias_limite: int = 30) -> int:
        """Limpia datos antiguos del estado"""
        try:
            from datetime import timedelta
            
            items_limpiados = 0
            cutoff_date = datetime.now() - timedelta(days=dias_limite)
            
            # Limpiar breakout_history
            if 'breakout_history' in self.estado_cache:
                items_antes = len(self.estado_cache['breakout_history'])
                self.estado_cache['breakout_history'] = {
                    k: v for k, v in self.estado_cache['breakout_history'].items()
                    if isinstance(v, datetime) and v > cutoff_date
                }
                items_limpiados += items_antes - len(self.estado_cache['breakout_history'])
            
            # Limpiar breakouts_detectados
            if 'breakouts_detectados' in self.estado_cache:
                items_antes = len(self.estado_cache['breakouts_detectados'])
                self.estado_cache['breakouts_detectados'] = {
                    k: v for k, v in self.estado_cache['breakouts_detectados'].items()
                    if isinstance(v, dict) and 'timestamp' in v and 
                    isinstance(v['timestamp'], datetime) and v['timestamp'] > cutoff_date
                }
                items_limpiados += items_antes - len(self.estado_cache['breakouts_detectados'])
            
            if items_limpiados > 0:
                logger.info(f"🗑️ Limpiados {items_limpiados} elementos antiguos del estado")
            
            return items_limpiados
            
        except Exception as e:
            logger.error(f"❌ Error limpiando estado antiguo: {e}")
            return 0
    
    def backup_estado(self) -> Optional[str]:
        """Crea backup del estado actual"""
        try:
            if not os.path.exists(self.estado_file):
                logger.warning("⚠️ No existe archivo de estado para respaldar")
                return None
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"estado_backup_{timestamp}.json"
            backup_path = os.path.join(os.path.dirname(self.estado_file), backup_filename)
            
            # Copiar archivo actual
            import shutil
            shutil.copy2(self.estado_file, backup_path)
            
            logger.info(f"💾 Backup creado: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return None
    
    def get_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del estado"""
        try:
            stats = {
                'archivo_estado': self.estado_file,
                'archivo_existe': os.path.exists(self.estado_file),
                'tamaño_cache': len(self.estado_cache),
                'operaciones_activas': len(self.estado_cache.get('operaciones_activas', {})),
                'esperando_reentry': len(self.estado_cache.get('esperando_reentry', {})),
                'breakouts_detectados': len(self.estado_cache.get('breakouts_detectados', {})),
                'total_operaciones': self.estado_cache.get('total_operaciones', 0)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}

# Instancia global del gestor de estado
state_manager = StateManager()

def get_state_manager() -> StateManager:
    """Obtiene la instancia global del gestor de estado"""
    return state_manager