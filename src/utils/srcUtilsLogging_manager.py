"""
Gestor de Logging
Configura y maneja el sistema de logging del bot
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional
from ..config.settings import LOGS_DIR, LOG_LEVEL, LOG_FORMAT, LOG_FILE_FORMAT

class LoggingManager:
    """Gestor centralizado de logging"""
    
    def __init__(self, name: str = "trading_bot"):
        """Inicializa el gestor de logging"""
        self.logger_name = name
        self.setup_logging()
    
    def setup_logging(self):
        """Configura el sistema de logging"""
        try:
            # Crear directorio de logs si no existe
            os.makedirs(LOGS_DIR, exist_ok=True)
            
            # Configurar logger principal
            logger = logging.getLogger(self.logger_name)
            logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
            
            # Limpiar handlers existentes
            logger.handlers.clear()
            
            # Formato para archivos
            file_formatter = logging.Formatter(LOG_FORMAT)
            
            # Handler para archivo con rotación diaria
            log_filename = datetime.now().strftime(LOG_FILE_FORMAT)
            log_path = os.path.join(LOGS_DIR, log_filename)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_path, 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=30,  # Mantener 30 días de logs
                encoding='utf-8'
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.DEBUG)
            logger.addHandler(file_handler)
            
            # Handler para consola
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(logging.INFO)
            logger.addHandler(console_handler)
            
            # Handler para errores críticos en archivo separado
            error_log_path = os.path.join(LOGS_DIR, 'errors.log')
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_path,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=90,  # Mantener 90 días de errores
                encoding='utf-8'
            )
            error_handler.setFormatter(file_formatter)
            error_handler.setLevel(logging.ERROR)
            logger.addHandler(error_handler)
            
            logger.info("✅ Sistema de logging configurado correctamente")
            logger.info(f"📁 Logs en: {LOGS_DIR}")
            
        except Exception as e:
            print(f"❌ Error configurando logging: {e}")
            # Fallback a logging básico
            logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Obtiene un logger"""
        if name:
            return logging.getLogger(f"{self.logger_name}.{name}")
        return logging.getLogger(self.logger_name)
    
    def log_system_info(self):
        """Log información del sistema"""
        try:
            logger = self.get_logger()
            logger.info("=" * 60)
            logger.info("🤖 SISTEMA DE TRADING BOT INICIADO")
            logger.info("=" * 60)
            logger.info(f"🕒 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"📁 Directorio logs: {LOGS_DIR}")
            logger.info(f"📊 Nivel de log: {LOG_LEVEL}")
            logger.info("=" * 60)
        except Exception as e:
            print(f"❌ Error loggeando info del sistema: {e}")

# Instancia global del gestor de logging
logging_manager = LoggingManager()

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Obtiene un logger configurado"""
    return logging_manager.get_logger(name)

def setup_logging():
    """Configura el sistema de logging"""
    logging_manager.setup_logging()
    logging_manager.log_system_info()