"""
Generador de Señales de Trading
**REGLA DE ORO: NO MODIFICAR LA LÓGICA ORIGINAL**
Código copiado íntegramente del archivo original
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..config.settings import *
from ..bot.telegram_bot import get_telegram_bot

logger = logging.getLogger(__name__)

class SignalGenerator:
    """
    Generador de Señales - LÓGICA ORIGINAL INTACTA
    NO MODIFICAR ESTE CÓDIGO
    """
    
    def __init__(self):
        """Inicializa el generador de señales"""
        self.telegram_bot = get_telegram_bot()
        self.senales_enviadas = set()
        logger.info("📊 SignalGenerator inicializado")
    
    def generar_senal_operacion(self, simbolo: str, tipo_operacion: str, precio_entrada: float, 
                              tp: float, sl: float, info_canal: Dict, datos_mercado: Dict, 
                              config_optima: Dict, breakout_info: Dict = None) -> bool:
        """
        Genera y envía señal de operación - LÓGICA ORIGINAL INTACTA
        """
        try:
            if simbolo in self.senales_enviadas:
                logger.warning(f"⚠️ Señal ya enviada para {simbolo}")
                return False
                
            if precio_entrada is None or tp is None or sl is None:
                logger.warning(f"    ❌ Niveles inválidos para {simbolo}, omitiendo señal")
                return False
                
            logger.info(f"🎯 Generando señal {tipo_operacion} para {simbolo}")
            
            # Enviar señal por Telegram
            exito = self.telegram_bot.enviar_senal_operacion(
                simbolo, tipo_operacion, precio_entrada, tp, sl, 
                info_canal, datos_mercado, config_optima, breakout_info
            )
            
            if exito:
                self.senales_enviadas.add(simbolo)
                logger.info(f"✅ Señal {tipo_operacion} para {simbolo} generada y enviada")
                return True
            else:
                logger.warning(f"⚠️ Error enviando señal para {simbolo}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error generando señal para {simbolo}: {e}")
            return False
    
    def enviar_alerta_breakout(self, simbolo: str, tipo_breakout: str, info_canal: Dict, 
                             datos_mercado: Dict, config_optima: Dict) -> bool:
        """
        Envía alerta de breakout - LÓGICA ORIGINAL INTACTA
        """
        try:
            logger.info(f"🚀 Enviando alerta de breakout para {simbolo}")
            
            exito = self.telegram_bot.enviar_alerta_breakout(
                simbolo, tipo_breakout, info_canal, datos_mercado, config_optima
            )
            
            if exito:
                logger.info(f"✅ Alerta de breakout enviada para {simbolo}")
            else:
                logger.warning(f"⚠️ Error enviando alerta de breakout para {simbolo}")
                
            return exito
            
        except Exception as e:
            logger.error(f"❌ Error enviando alerta de breakout: {e}")
            return False
    
    def limpiar_senales_antiguas(self, horas_limite: int = 2) -> None:
        """Limpia señales antiguas para permitir nuevas entradas"""
        try:
            # Por ahora solo resetear el set
            # En una implementación más sofisticada, se podría usar timestamps
            self.senales_enviadas.clear()
            logger.info(f"🗑️ Señales limpiadas (límite: {horas_limite} horas)")
        except Exception as e:
            logger.error(f"❌ Error limpiando señales: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del generador"""
        return {
            'senales_enviadas_count': len(self.senales_enviadas),
            'senales_enviadas': list(self.senales_enviadas)
        }

# Instancia global del generador de señales
signal_generator = SignalGenerator()

def get_signal_generator() -> SignalGenerator:
    """Obtiene la instancia global del generador de señales"""
    return signal_generator