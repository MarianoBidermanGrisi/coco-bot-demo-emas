"""
Manejo de Variables de Entorno
Carga y valida todas las variables de entorno para Render.com
"""

import os
import logging
from typing import List, Optional, Dict, Any
from .settings import *

logger = logging.getLogger(__name__)

class EnvironmentManager:
    """Gestor centralizado de variables de entorno"""
    
    def __init__(self):
        """Inicializa el gestor de entorno"""
        self._telegram_token: Optional[str] = None
        self._telegram_chat_ids: List[str] = []
        self._webhook_url: Optional[str] = None
        self._render_external_url: Optional[str] = None
        self._config_loaded = False
        self._load_environment()
    
    def _load_environment(self) -> None:
        """Carga todas las variables de entorno"""
        try:
            logger.info("🔧 Cargando variables de entorno...")
            
            # Cargar token de Telegram
            self._telegram_token = self._get_env_var('TELEGRAM_TOKEN', required=False)
            if self._telegram_token:
                logger.info("✅ TELEGRAM_TOKEN cargado correctamente")
            else:
                logger.warning("⚠️ TELEGRAM_TOKEN no encontrado - Telegram deshabilitado")
            
            # Cargar Chat IDs
            self._telegram_chat_ids = self._get_telegram_chat_ids()
            if self._telegram_chat_ids:
                logger.info(f"✅ TELEGRAM_CHAT_IDS cargados: {len(self._telegram_chat_ids)} chats")
            else:
                logger.warning("⚠️ TELEGRAM_CHAT_IDS no encontrados - usando por defecto")
                self._telegram_chat_ids = DEFAULT_CHAT_IDS
            
            # Cargar URLs de webhook
            self._webhook_url = self._get_env_var('WEBHOOK_URL', required=False)
            self._render_external_url = self._get_env_var('RENDER_EXTERNAL_URL', required=False)
            
            if self._webhook_url:
                logger.info(f"✅ WEBHOOK_URL configurado: {self._webhook_url}")
            elif self._render_external_url:
                logger.info(f"✅ RENDER_EXTERNAL_URL detectado: {self._render_external_url}")
            else:
                logger.warning("⚠️ URLs de webhook no configuradas")
            
            # Validar configuración
            self._validate_configuration()
            
            self._config_loaded = True
            logger.info("✅ Variables de entorno cargadas correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error cargando variables de entorno: {e}")
            raise
    
    def _get_env_var(self, name: str, required: bool = False, default: Optional[str] = None) -> Optional[str]:
        """Obtiene una variable de entorno"""
        try:
            value = os.environ.get(name, default)
            if required and not value:
                raise ValueError(f"Variable de entorno requerida no encontrada: {name}")
            return value
        except Exception as e:
            if required:
                raise
            logger.warning(f"⚠️ Error obteniendo {name}: {e}")
            return default
    
    def _get_telegram_chat_ids(self) -> List[str]:
        """Obtiene y valida los Chat IDs de Telegram"""
        try:
            chat_ids_str = os.environ.get('TELEGRAM_CHAT_ID', '')
            if not chat_ids_str:
                return []
            
            # Parsear lista de chat IDs (separados por comas)
            chat_ids = [cid.strip() for cid in chat_ids_str.split(',') if cid.strip()]
            
            # Validar formato de chat IDs
            valid_chat_ids = []
            for chat_id in chat_ids:
                try:
                    # Chat ID debe ser numérico (incluyendo negativos)
                    int(chat_id)
                    valid_chat_ids.append(chat_id)
                except ValueError:
                    logger.warning(f"⚠️ Chat ID inválido ignorado: {chat_id}")
            
            return valid_chat_ids
            
        except Exception as e:
            logger.error(f"❌ Error procesando TELEGRAM_CHAT_ID: {e}")
            return []
    
    def _validate_configuration(self) -> None:
        """Valida que la configuración sea correcta"""
        try:
            errors = []
            
            # Validar token de Telegram si está presente
            if self._telegram_token and len(self._telegram_token) < 10:
                errors.append("TELEGRAM_TOKEN parece ser inválido (muy corto)")
            
            # Validar chat IDs
            if not self._telegram_chat_ids:
                errors.append("No hay chat IDs configurados")
            else:
                for chat_id in self._telegram_chat_ids:
                    if not chat_id.lstrip('-').isdigit():
                        errors.append(f"Chat ID inválido: {chat_id}")
            
            # Validar URLs si están configuradas
            if self._webhook_url and not self._webhook_url.startswith(('http://', 'https://')):
                errors.append("WEBHOOK_URL debe ser una URL válida")
            
            if self._render_external_url and not self._render_external_url.startswith(('http://', 'https://')):
                errors.append("RENDER_EXTERNAL_URL debe ser una URL válida")
            
            if errors:
                raise ValueError(f"Errores de configuración: {'; '.join(errors)}")
            
            logger.info("✅ Configuración validada correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en validación de configuración: {e}")
            raise
    
    def get_telegram_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de Telegram"""
        return {
            'token': self._telegram_token,
            'chat_ids': self._telegram_chat_ids,
            'webhook_url': self._webhook_url,
            'render_external_url': self._render_external_url
        }
    
    def get_trading_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de trading"""
        return {
            'symbols': DEFAULT_SYMBOLS,
            'timeframes': DEFAULT_TIMEFRAMES,
            'velas_options': DEFAULT_VELAS_OPTIONS,
            'min_channel_width_percent': MIN_CHANNEL_WIDTH_PERCENT,
            'trend_threshold_degrees': TREND_THRESHOLD_DEGREES,
            'min_trend_strength_degrees': MIN_TREND_STRENGTH_DEGREES,
            'entry_margin': ENTRY_MARGIN,
            'min_rr_ratio': MIN_RR_RATIO,
            'scan_interval_minutes': SCAN_INTERVAL_MINUTES,
            'auto_optimize': AUTO_OPTIMIZE,
            'min_samples_optimizacion': MIN_SAMPLES_OPTIMIZACION,
            'reevaluacion_horas': REEVALUACION_HORAS
        }
    
    def get_file_config(self) -> Dict[str, str]:
        """Obtiene la configuración de archivos"""
        return {
            'log_path': OPERACIONES_LOG_FILE,
            'estado_file': ESTADO_BOT_FILE,
            'ultimo_reporte_file': ULTIMO_REPORTE_FILE,
            'mejores_parametros_file': MEJORES_PARAMETROS_FILE
        }
    
    def is_configured(self) -> bool:
        """Verifica si la configuración está completa"""
        return self._config_loaded
    
    def is_telegram_enabled(self) -> bool:
        """Verifica si Telegram está habilitado"""
        return bool(self._telegram_token and self._telegram_chat_ids)
    
    def get_webhook_url(self) -> Optional[str]:
        """Obtiene la URL del webhook"""
        if self._webhook_url:
            return self._webhook_url
        elif self._render_external_url:
            return f"{self._render_external_url}/webhook"
        return None
    
    def print_configuration_summary(self) -> None:
        """Imprime un resumen de la configuración"""
        print("\n" + "=" * 60)
        print("🤖 CONFIGURACIÓN DEL BOT DE TRADING")
        print("=" * 60)
        print(f"📱 Telegram: {'✅ Habilitado' if self.is_telegram_enabled() else '❌ Deshabilitado'}")
        print(f"🔗 Webhook URL: {self.get_webhook_url() or 'No configurado'}")
        print(f"💱 Símbolos: {len(DEFAULT_SYMBOLS)} pares")
        print(f"⏰ Timeframes: {', '.join(DEFAULT_TIMEFRAMES)}")
        print(f"🕯️ Velas: {DEFAULT_VELAS_OPTIONS}")
        print(f"📊 Auto-optimización: {'✅ Activada' if AUTO_OPTIMIZE else '❌ Desactivada'}")
        print("=" * 60)

# Instancia global del gestor de entorno
env_manager = EnvironmentManager()

# Funciones de conveniencia para acceder a la configuración
def get_env_manager() -> EnvironmentManager:
    """Obtiene la instancia global del gestor de entorno"""
    return env_manager

def get_telegram_config() -> Dict[str, Any]:
    """Obtiene la configuración de Telegram"""
    return env_manager.get_telegram_config()

def get_trading_config() -> Dict[str, Any]:
    """Obtiene la configuración de trading"""
    return env_manager.get_trading_config()

def get_file_config() -> Dict[str, str]:
    """Obtiene la configuración de archivos"""
    return env_manager.get_file_config()
