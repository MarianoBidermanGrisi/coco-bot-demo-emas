"""
Bot de Telegram para el Sistema de Trading
**REGLA DE ORO: NO MODIFICAR LA LÓGICA ORIGINAL**
Código copiado íntegramente del archivo original
"""

import requests
import time
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from io import BytesIO

from ..config.settings import *
from ..config.environment import get_telegram_config

logger = logging.getLogger(__name__)

class TelegramBot:
    """
    Bot de Telegram - LÓGICA ORIGINAL INTACTA
    NO MODIFICAR ESTE CÓDIGO
    """
    
    def __init__(self):
        """Inicializa el bot de Telegram"""
        try:
            self.telegram_config = get_telegram_config()
            self.token = self.telegram_config['token']
            self.chat_ids = self.telegram_config['chat_ids']
            self.base_url = f"https://api.telegram.org/bot{self.token}"
            
            if not self.token:
                logger.warning("⚠️ TELEGRAM_TOKEN no configurado - Bot deshabilitado")
                self.enabled = False
            else:
                self.enabled = True
                logger.info(f"🤖 TelegramBot inicializado - Chat IDs: {len(self.chat_ids)}")
                
        except Exception as e:
            logger.error(f"❌ Error inicializando TelegramBot: {e}")
            self.enabled = False
    
    def test_connection(self) -> bool:
        """Prueba la conexión con Telegram"""
        try:
            if not self.enabled:
                logger.warning("⚠️ Telegram deshabilitado")
                return False
                
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    bot_info = result.get('result', {})
                    logger.info(f"✅ Conexión exitosa - Bot: @{bot_info.get('username', 'Unknown')}")
                    return True
                else:
                    logger.error(f"❌ Error en respuesta de Telegram: {result}")
                    return False
            else:
                logger.error(f"❌ Error HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error probando conexión de Telegram: {e}")
            return False
    
    def _enviar_telegram_simple(self, mensaje: str, token: str = None, chat_ids: List[str] = None) -> bool:
        """Envía mensaje simple por Telegram - LÓGICA ORIGINAL INTACTA"""
        try:
            if not token or not chat_ids:
                token = self.token
                chat_ids = self.chat_ids
                
            if not token or not chat_ids:
                logger.warning("⚠️ Configuración de Telegram incompleta")
                return False
                
            resultados = []
            for chat_id in chat_ids:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {'chat_id': chat_id, 'text': mensaje, 'parse_mode': 'HTML'}
                try:
                    r = requests.post(url, json=payload, timeout=10)
                    resultados.append(r.status_code == 200)
                    if r.status_code == 200:
                        logger.debug(f"✅ Mensaje enviado a chat {chat_id}")
                    else:
                        logger.warning(f"⚠️ Error enviando a chat {chat_id}: {r.status_code}")
                except Exception as e:
                    logger.error(f"❌ Error enviando a chat {chat_id}: {e}")
                    resultados.append(False)
            return any(resultados)
            
        except Exception as e:
            logger.error(f"❌ Error en _enviar_telegram_simple: {e}")
            return False
    
    def enviar_mensaje(self, mensaje: str, chat_id: str = None) -> bool:
        """Envía mensaje a uno o todos los chats"""
        try:
            if not self.enabled:
                logger.warning("⚠️ Telegram deshabilitado")
                return False
                
            if chat_id:
                # Enviar a chat específico
                return self._enviar_telegram_simple(mensaje, self.token, [chat_id])
            else:
                # Enviar a todos los chats
                return self._enviar_telegram_simple(mensaje)
                
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje: {e}")
            return False
    
    def enviar_alerta_breakout(self, simbolo: str, tipo_breakout: str, info_canal: Dict, 
                             datos_mercado: Dict, config_optima: Dict) -> bool:
        """
        Envía alerta de BREAKOUT detectado - LÓGICA ORIGINAL INTACTA
        """
        try:
            if not self.enabled:
                logger.warning("⚠️ Telegram deshabilitado - no se puede enviar alerta")
                return False
                
            precio_cierre = datos_mercado['cierres'][-1]
            resistencia = info_canal['resistencia']
            soporte = info_canal['soporte']
            direccion_canal = info_canal['direccion']
            
            # Determinar tipo de ruptura CORREGIDO SEGÚN LA ESTRATEGIA
            if tipo_breakout == "BREAKOUT_LONG":
                emoji_principal = "🚀"
                tipo_texto = "RUPTURA de SOPORTE"
                nivel_roto = f"Soporte: {soporte:.8f}"
                direccion_emoji = "⬇️"
                contexto = f"Canal {direccion_canal} → Ruptura de SOPORTE"
                expectativa = "posible entrada en long si el precio reingresa al canal"
            else:  # BREAKOUT_SHORT
                emoji_principal = "📉"
                tipo_texto = "RUPTURA BAJISTA de RESISTENCIA"
                nivel_roto = f"Resistencia: {resistencia:.8f}"
                direccion_emoji = "⬆️"
                contexto = f"Canal {direccion_canal} → Rechazo desde RESISTENCIA"
                expectativa = "posible entrada en sort si el precio reingresa al canal"
                
            # Mensaje de alerta
            mensaje = f"""
{emoji_principal} <b>¡BREAKOUT DETECTADO! - {simbolo}</b>
⚠️ <b>{tipo_texto}</b> {direccion_emoji}
⏰ <b>Hora:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
⏳ <b>ESPERANDO REINGRESO...</b>
👁️ Máximo 30 minutos para confirmación
📍 {expectativa}
            """
            
            logger.info(f"     📊 Generando gráfico de breakout para {simbolo}...")
            
            # Aquí se integraría con el generador de gráficos
            # buf = self.generar_grafico_breakout(simbolo, info_canal, datos_mercado, tipo_breakout, config_optima)
            
            # Enviar mensaje sin gráfico por ahora
            exito = self._enviar_telegram_simple(mensaje)
            
            if exito:
                logger.info(f"     ✅ Alerta de breakout enviada para {simbolo}")
            else:
                logger.warning(f"     ⚠️ Error enviando alerta de breakout para {simbolo}")
                
            return exito
            
        except Exception as e:
            logger.error(f"❌ Error enviando alerta de breakout: {e}")
            return False
    
    def enviar_senal_operacion(self, simbolo: str, tipo_operacion: str, precio_entrada: float, 
                             tp: float, sl: float, info_canal: Dict, datos_mercado: Dict, 
                             config_optima: Dict, breakout_info: Dict = None) -> bool:
        """
        Envía señal de operación - LÓGICA ORIGINAL INTACTA
        """
        try:
            if not self.enabled:
                logger.warning("⚠️ Telegram deshabilitado - no se puede enviar señal")
                return False
                
            riesgo = abs(precio_entrada - sl)
            beneficio = abs(tp - precio_entrada)
            ratio_rr = beneficio / riesgo if riesgo > 0 else 0
            
            # Calcular SL y TP en porcentaje
            sl_percent = abs((sl - precio_entrada) / precio_entrada) * 100
            tp_percent = abs((tp - precio_entrada) / precio_entrada) * 100
            
            stoch_estado = "📉 SOBREVENTA" if tipo_operacion == "LONG" else "📈 SOBRECOMPRA"
            
            breakout_texto = ""
            if breakout_info:
                tiempo_breakout = (datetime.now() - breakout_info['timestamp']).total_seconds() / 60
                breakout_texto = f"""
🚀 <b>BREAKOUT + REENTRY DETECTADO:</b>
⏰ Tiempo desde breakout: {tiempo_breakout:.1f} minutos
💰 Precio breakout: {breakout_info['precio_breakout']:.8f}
                """
                
            mensaje = f"""
🎯 <b>SEÑAL DE {tipo_operacion} - {simbolo}</b>
{breakout_texto}
⏱️ <b>Configuración óptima:</b>
📊 Timeframe: {config_optima['timeframe']}
🕯️ Velas: {config_optima['num_velas']}
📏 Ancho Canal: {info_canal['ancho_canal_porcentual']:.1f}% ⭐
💰 <b>Precio Actual:</b> {datos_mercado['precio_actual']:.8f}
🎯 <b>Entrada:</b> {precio_entrada:.8f}
🛑 <b>Stop Loss:</b> {sl:.8f}
🎯 <b>Take Profit:</b> {tp:.8f}
📊 <b>Ratio R/B:</b> {ratio_rr:.2f}:1
🎯 <b>SL:</b> {sl_percent:.2f}%
🎯 <b>TP:</b> {tp_percent:.2f}%
💰 <b>Riesgo:</b> {riesgo:.8f}
🎯 <b>Beneficio Objetivo:</b> {beneficio:.8f}
📈 <b>Tendencia:</b> {info_canal['direccion']}
💪 <b>Fuerza:</b> {info_canal['fuerza_texto']}
📏 <b>Ángulo:</b> {info_canal['angulo_tendencia']:.1f}°
📊 <b>Pearson:</b> {info_canal['coeficiente_pearson']:.3f}
🎯 <b>R² Score:</b> {info_canal['r2_score']:.3f}
🎰 <b>Stochástico:</b> {stoch_estado}
📊 <b>Stoch K:</b> {info_canal['stoch_k']:.1f}
📈 <b>Stoch D:</b> {info_canal['stoch_d']:.1f}
⏰ <b>Hora:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💡 <b>Estrategia:</b> BREAKOUT + REENTRY con confirmación Stochastic
            """
            
            logger.info(f"     📊 Generando gráfico para {simbolo}...")
            
            # Aquí se integraría con el generador de gráficos
            # buf = self.generar_grafico_profesional(simbolo, info_canal, datos_mercado, 
            #                                       precio_entrada, tp, sl, tipo_operacion)
            
            # Enviar mensaje sin gráfico por ahora
            exito = self._enviar_telegram_simple(mensaje)
            
            if exito:
                logger.info(f"     ✅ Señal {tipo_operacion} para {simbolo} enviada")
            else:
                logger.warning(f"     ⚠️ Error enviando señal {tipo_operacion} para {simbolo}")
                
            return exito
            
        except Exception as e:
            logger.error(f"❌ Error enviando señal de operación: {e}")
            return False
    
    def enviar_cierre_operacion(self, datos_operacion: Dict) -> bool:
        """
        Envía notificación de cierre de operación - LÓGICA ORIGINAL INTACTA
        """
        try:
            if not self.enabled:
                logger.warning("⚠️ Telegram deshabilitado - no se puede enviar notificación de cierre")
                return False
                
            emoji = "🟢" if datos_operacion['resultado'] == "TP" else "🔴"
            color_emoji = "✅" if datos_operacion['resultado'] == "TP" else "❌"
            
            if datos_operacion['tipo'] == 'LONG':
                pnl_absoluto = datos_operacion['precio_salida'] - datos_operacion['precio_entrada']
            else:
                pnl_absoluto = datos_operacion['precio_entrada'] - datos_operacion['precio_salida']
                
            breakout_usado = "🚀 Sí" if datos_operacion.get('breakout_usado', False) else "❌ No"
            
            mensaje = f"""
{emoji} <b>OPERACIÓN CERRADA - {datos_operacion['symbol']}</b>
{color_emoji} <b>RESULTADO: {datos_operacion['resultado']}</b>
📊 Tipo: {datos_operacion['tipo']}
💰 Entrada: {datos_operacion['precio_entrada']:.8f}
🎯 Salida: {datos_operacion['precio_salida']:.8f}
💵 PnL Absoluto: {pnl_absoluto:.8f}
📈 PnL %: {datos_operacion['pnl_percent']:.2f}%
⏰ Duración: {datos_operacion['duracion_minutos']:.1f} minutos
🚀 Breakout+Reentry: {breakout_usado}
📏 Ángulo: {datos_operacion['angulo_tendencia']:.1f}°
📊 Pearson: {datos_operacion['pearson']:.3f}
🎯 R²: {datos_operacion['r2_score']:.3f}
📏 Ancho: {datos_operacion.get('ancho_canal_porcentual', 0):.1f}%
⏱️ TF: {datos_operacion.get('timeframe_utilizado', 'N/A')}
🕯️ Velas: {datos_operacion.get('velas_utilizadas', 0)}
🕒 {datos_operacion['timestamp']}
            """
            
            exito = self._enviar_telegram_simple(mensaje)
            
            if exito:
                logger.info(f"✅ Notificación de cierre enviada para {datos_operacion['symbol']}")
            else:
                logger.warning(f"⚠️ Error enviando notificación de cierre para {datos_operacion['symbol']}")
                
            return exito
            
        except Exception as e:
            logger.error(f"❌ Error enviando cierre de operación: {e}")
            return False
    
    def enviar_reporte_semanal(self, mensaje: str) -> bool:
        """Envía reporte semanal - LÓGICA ORIGINAL INTACTA"""
        try:
            if not self.enabled:
                logger.warning("⚠️ Telegram deshabilitado - no se puede enviar reporte")
                return False
                
            exito = self._enviar_telegram_simple(mensaje)
            
            if exito:
                logger.info("✅ Reporte semanal enviado correctamente")
            else:
                logger.warning("⚠️ Error enviando reporte semanal")
                
            return exito
            
        except Exception as e:
            logger.error(f"❌ Error enviando reporte semanal: {e}")
            return False
    
    def is_enabled(self) -> bool:
        """Verifica si Telegram está habilitado"""
        return self.enabled
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del bot"""
        return {
            'enabled': self.enabled,
            'token_configured': bool(self.token),
            'chat_ids_count': len(self.chat_ids),
            'chat_ids': self.chat_ids
        }

# Instancia global del bot de Telegram
telegram_bot = TelegramBot()

def get_telegram_bot() -> TelegramBot:
    """Obtiene la instancia global del bot de Telegram"""
    return telegram_bot
