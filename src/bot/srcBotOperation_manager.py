"""
Gestor de Operaciones de Trading
**REGLA DE ORO: NO MODIFICAR LA LÓGICA ORIGINAL**
Código copiado íntegramente del archivo original
"""

import csv
import os
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from ..config.settings import *
from ..bot.telegram_bot import get_telegram_bot

logger = logging.getLogger(__name__)

class OperationManager:
    """
    Gestor de Operaciones - LÓGICA ORIGINAL INTACTA
    NO MODIFICAR ESTE CÓDIGO
    """
    
    def __init__(self, log_path: str, estado_file: str):
        """Inicializa el gestor de operaciones"""
        self.log_path = log_path
        self.estado_file = estado_file
        self.operaciones_activas = {}
        self.telegram_bot = get_telegram_bot()
        self.inicializar_log()
        logger.info("📋 OperationManager inicializado")
    
    def inicializar_log(self):
        """Inicializa archivo de log - LÓGICA ORIGINAL INTACTA"""
        try:
            if not os.path.exists(self.log_path):
                with open(self.log_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'timestamp', 'symbol', 'tipo', 'precio_entrada',
                        'take_profit', 'stop_loss', 'precio_salida',
                        'resultado', 'pnl_percent', 'duracion_minutos',
                        'angulo_tendencia', 'pearson', 'r2_score',
                        'ancho_canal_relativo', 'ancho_canal_porcentual',
                        'nivel_fuerza', 'timeframe_utilizado', 'velas_utilizadas',
                        'stoch_k', 'stoch_d', 'breakout_usado'
                    ])
                logger.info(f"✅ Archivo de log inicializado: {self.log_path}")
        except Exception as e:
            logger.error(f"❌ Error inicializando log: {e}")
    
    def registrar_operacion(self, datos_operacion: Dict) -> bool:
        """Registra operación en CSV - LÓGICA ORIGINAL INTACTA"""
        try:
            with open(self.log_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datos_operacion['timestamp'],
                    datos_operacion['symbol'],
                    datos_operacion['tipo'],
                    datos_operacion['precio_entrada'],
                    datos_operacion['take_profit'],
                    datos_operacion['stop_loss'],
                    datos_operacion['precio_salida'],
                    datos_operacion['resultado'],
                    datos_operacion['pnl_percent'],
                    datos_operacion['duracion_minutos'],
                    datos_operacion['angulo_tendencia'],
                    datos_operacion['pearson'],
                    datos_operacion['r2_score'],
                    datos_operacion.get('ancho_canal_relativo', 0),
                    datos_operacion.get('ancho_canal_porcentual', 0),
                    datos_operacion.get('nivel_fuerza', 1),
                    datos_operacion.get('timeframe_utilizado', 'N/A'),
                    datos_operacion.get('velas_utilizadas', 0),
                    datos_operacion.get('stoch_k', 0),
                    datos_operacion.get('stoch_d', 0),
                    datos_operacion.get('breakout_usado', False)
                ])
            logger.info(f"✅ Operación registrada: {datos_operacion['symbol']} - {datos_operacion['resultado']}")
            return True
        except Exception as e:
            logger.error(f"❌ Error registrando operación: {e}")
            return False
    
    def agregar_operacion_activa(self, simbolo: str, operacion: Dict) -> None:
        """Agrega operación activa"""
        try:
            self.operaciones_activas[simbolo] = operacion
            logger.info(f"➕ Operación activa agregada: {simbolo}")
        except Exception as e:
            logger.error(f"❌ Error agregando operación activa: {e}")
    
    def eliminar_operacion_activa(self, simbolo: str) -> bool:
        """Elimina operación activa"""
        try:
            if simbolo in self.operaciones_activas:
                del self.operaciones_activas[simbolo]
                logger.info(f"➖ Operación activa eliminada: {simbolo}")
                return True
            else:
                logger.warning(f"⚠️ Operación activa no encontrada: {simbolo}")
                return False
        except Exception as e:
            logger.error(f"❌ Error eliminando operación activa: {e}")
            return False
    
    def get_operaciones_activas(self) -> Dict[str, Dict]:
        """Obtiene operaciones activas"""
        return self.operaciones_activas.copy()
    
    def get_operaciones_activas_count(self) -> int:
        """Obtiene número de operaciones activas"""
        return len(self.operaciones_activas)
    
    def verificar_cierre_operaciones(self, obtener_precio_actual_func) -> List[str]:
        """Verifica cierre de operaciones - LÓGICA ORIGINAL INTACTA"""
        operaciones_cerradas = []
        try:
            for simbolo, operacion in list(self.operaciones_activas.items()):
                try:
                    precio_actual = obtener_precio_actual_func(simbolo)
                    if precio_actual is None:
                        logger.warning(f"⚠️ No se pudo obtener precio para {simbolo}")
                        continue
                        
                    tp = operacion['take_profit']
                    sl = operacion['stop_loss']
                    tipo = operacion['tipo']
                    resultado = None
                    
                    if tipo == "LONG":
                        if precio_actual >= tp:
                            resultado = "TP"
                        elif precio_actual <= sl:
                            resultado = "SL"
                    else:  # SHORT
                        if precio_actual <= tp:
                            resultado = "TP"
                        elif precio_actual >= sl:
                            resultado = "SL"
                    
                    if resultado:
                        # Calcular PnL
                        if tipo == "LONG":
                            pnl_percent = ((precio_actual - operacion['precio_entrada']) / operacion['precio_entrada']) * 100
                        else:
                            pnl_percent = ((operacion['precio_entrada'] - precio_actual) / operacion['precio_entrada']) * 100
                        
                        # Calcular duración
                        tiempo_entrada = datetime.fromisoformat(operacion['timestamp_entrada'])
                        duracion_minutos = (datetime.now() - tiempo_entrada).total_seconds() / 60
                        
                        datos_operacion = {
                            'timestamp': datetime.now().isoformat(),
                            'symbol': simbolo,
                            'tipo': tipo,
                            'precio_entrada': operacion['precio_entrada'],
                            'take_profit': tp,
                            'stop_loss': sl,
                            'precio_salida': precio_actual,
                            'resultado': resultado,
                            'pnl_percent': pnl_percent,
                            'duracion_minutos': duracion_minutos,
                            'angulo_tendencia': operacion.get('angulo_tendencia', 0),
                            'pearson': operacion.get('pearson', 0),
                            'r2_score': operacion.get('r2_score', 0),
                            'ancho_canal_relativo': operacion.get('ancho_canal_relativo', 0),
                            'ancho_canal_porcentual': operacion.get('ancho_canal_porcentual', 0),
                            'nivel_fuerza': operacion.get('nivel_fuerza', 1),
                            'timeframe_utilizado': operacion.get('timeframe_utilizado', 'N/A'),
                            'velas_utilizadas': operacion.get('velas_utilizadas', 0),
                            'stoch_k': operacion.get('stoch_k', 0),
                            'stoch_d': operacion.get('stoch_d', 0),
                            'breakout_usado': operacion.get('breakout_usado', False)
                        }
                        
                        # Registrar operación
                        self.registrar_operacion(datos_operacion)
                        
                        # Enviar notificación de cierre
                        self.telegram_bot.enviar_cierre_operacion(datos_operacion)
                        
                        # Eliminar de operaciones activas
                        self.eliminar_operacion_activa(simbolo)
                        
                        operaciones_cerradas.append(simbolo)
                        logger.info(f"     📊 {simbolo} Operación {resultado} - PnL: {pnl_percent:.2f}%")
                        
                except Exception as e:
                    logger.error(f"❌ Error verificando cierre para {simbolo}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error en verificación de cierres: {e}")
            
        return operaciones_cerradas
    
    def filtrar_operaciones_ultima_semana(self) -> List[Dict]:
        """Filtra operaciones de los últimos 7 días - LÓGICA ORIGINAL INTACTA"""
        try:
            if not os.path.exists(self.log_path):
                return []
                
            ops_recientes = []
            fecha_limite = datetime.now() - timedelta(days=7)
            
            with open(self.log_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        timestamp = datetime.fromisoformat(row['timestamp'])
                        if timestamp >= fecha_limite:
                            ops_recientes.append({
                                'timestamp': timestamp,
                                'symbol': row['symbol'],
                                'resultado': row['resultado'],
                                'pnl_percent': float(row['pnl_percent']),
                                'tipo': row['tipo'],
                                'breakout_usado': row.get('breakout_usado', 'False') == 'True'
                            })
                    except Exception:
                        continue
                        
            return ops_recientes
            
        except Exception as e:
            logger.error(f"❌ Error filtrando operaciones: {e}")
            return []
    
    def generar_reporte_semanal(self) -> Optional[str]:
        """Genera reporte semanal - LÓGICA ORIGINAL INTACTA"""
        try:
            ops_ultima_semana = self.filtrar_operaciones_ultima_semana()
            if not ops_ultima_semana:
                return None
                
            total_ops = len(ops_ultima_semana)
            wins = sum(1 for op in ops_ultima_semana if op['resultado'] == 'TP')
            losses = sum(1 for op in ops_ultima_semana if op['resultado'] == 'SL')
            winrate = (wins/total_ops*100) if total_ops > 0 else 0
            pnl_total = sum(op['pnl_percent'] for op in ops_ultima_semana)
            mejor_op = max(ops_ultima_semana, key=lambda x: x['pnl_percent'])
            peor_op = min(ops_ultima_semana, key=lambda x: x['pnl_percent'])
            ganancias = [op['pnl_percent'] for op in ops_ultima_semana if op['pnl_percent'] > 0]
            perdidas = [abs(op['pnl_percent']) for op in ops_ultima_semana if op['pnl_percent'] < 0]
            avg_ganancia = sum(ganancias)/len(ganancias) if ganancias else 0
            avg_perdida = sum(perdidas)/len(perdidas) if perdidas else 0
            
            # Calcular racha actual
            racha_actual = 0
            for op in reversed(ops_ultima_semana):
                if op['resultado'] == 'TP':
                    racha_actual += 1
                else:
                    break
                    
            emoji_resultado = "🟢" if pnl_total > 0 else "🔴" if pnl_total < 0 else "⚪"
            
            mensaje = f"""
━━━━━━━━━━━━━━━━━━━━
📊 <b>REPORTE SEMANAL</b>
━━━━━━━━━━━━━━━━━━━━
📅 {datetime.now().strftime('%d/%m/%Y')} | Últimos 7 días
<b>RENDIMIENTO GENERAL</b>
{emoji_resultado} PnL Total: <b>{pnl_total:+.2f}%</b>
📈 Win Rate: <b>{winrate:.1f}%</b>
✅ Ganadas: {wins} | ❌ Perdidas: {losses}
<b>ESTADÍSTICAS</b>
📊 Operaciones: {total_ops}
💰 Ganancia Promedio: +{avg_ganancia:.2f}%
📉 Pérdida Promedio: -{avg_perdida:.2f}%
🔥 Racha actual: {racha_actual} wins
<b>DESTACADOS</b>
🏆 Mejor: {mejor_op['symbol']} ({mejor_op['tipo']})
   → {mejor_op['pnl_percent']:+.2f}%
⚠️ Peor: {peor_op['symbol']} ({peor_op['tipo']})
   → {peor_op['pnl_percent']:+.2f}%
━━━━━━━━━━━━━━━━━━━━
🤖 Bot automático 24/7
⚡ Estrategia: Breakout + Reentry
💎 Acceso Premium: @TuUsuario
            """
            
            return mensaje
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte semanal: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del gestor"""
        return {
            'operaciones_activas_count': len(self.operaciones_activas),
            'operaciones_activas': list(self.operaciones_activas.keys()),
            'log_path': self.log_path,
            'log_exists': os.path.exists(self.log_path)
        }

# Instancia global del gestor de operaciones
operation_manager = None

def get_operation_manager(log_path: str = None, estado_file: str = None) -> OperationManager:
    """Obtiene la instancia global del gestor de operaciones"""
    global operation_manager
    if operation_manager is None:
        if log_path is None:
            from ..config.settings import OPERACIONES_LOG_FILE
            log_path = OPERACIONES_LOG_FILE
        if estado_file is None:
            from ..config.settings import ESTADO_BOT_FILE
            estado_file = ESTADO_BOT_FILE
        operation_manager = OperationManager(log_path, estado_file)
    return operation_manager