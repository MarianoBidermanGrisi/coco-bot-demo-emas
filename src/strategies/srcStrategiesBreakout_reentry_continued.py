"""
Continuación de la Estrategia Breakout + Reentry
**REGLA DE ORO: NO MODIFICAR LA LÓGICA ORIGINAL**
Código copiado íntegramente del archivo original - Métodos adicionales
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

def detectar_reentry(self, simbolo, info_canal, datos_mercado):
    """Detecta si el precio ha REINGRESADO al canal - LÓGICA ORIGINAL INTACTA"""
    if simbolo not in self.esperando_reentry:
        return None
    breakout_info = self.esperando_reentry[simbolo]
    tipo_breakout = breakout_info['tipo']
    timestamp_breakout = breakout_info['timestamp']
    tiempo_desde_breakout = (datetime.now() - timestamp_breakout).total_seconds() / 60
    if tiempo_desde_breakout > 30:
        logger.info(f"     ⏰ {simbolo} - Timeout de reentry (>30 min), cancelando espera")
        del self.esperando_reentry[simbolo]
        # Limpiar también de breakouts_detectados cuando expira el reentry
        if simbolo in self.breakouts_detectados:
            del self.breakouts_detectados[simbolo]
        return None
    precio_actual = datos_mercado['precio_actual']
    resistencia = info_canal['resistencia']
    soporte = info_canal['soporte']
    stoch_k = info_canal['stoch_k']
    stoch_d = info_canal['stoch_d']
    tolerancia = 0.001 * precio_actual
    if tipo_breakout == "BREAKOUT_LONG":
        if soporte <= precio_actual <= resistencia:
            distancia_soporte = abs(precio_actual - soporte)
            if distancia_soporte <= tolerancia and stoch_k <= 30 and stoch_d <= 30:
                logger.info(f"     ✅ {simbolo} - REENTRY LONG confirmado! Entrada en soporte con Stoch oversold")
                # Limpiar breakouts_detectados cuando se confirma reentry
                if simbolo in self.breakouts_detectados:
                    del self.breakouts_detectados[simbolo]
                return "LONG"
    elif tipo_breakout == "BREAKOUT_SHORT":
        if soporte <= precio_actual <= resistencia:
            distancia_resistencia = abs(precio_actual - resistencia)
            if distancia_resistencia <= tolerancia and stoch_k >= 70 and stoch_d >= 70:
                logger.info(f"     ✅ {simbolo} - REENTRY SHORT confirmado! Entrada en resistencia con Stoch overbought")
                # Limpiar breakouts_detectados cuando se confirma reentry
                if simbolo in self.breakouts_detectados:
                    del self.breakouts_detectados[simbolo]
                return "SHORT"
    return None

def calcular_niveles_entrada(self, tipo_operacion, info_canal, precio_actual):
    """Calcula niveles de entrada - LÓGICA ORIGINAL INTACTA"""
    if not info_canal:
        return None, None, None
    resistencia = info_canal['resistencia']
    soporte = info_canal['soporte']
    ancho_canal = resistencia - soporte
    sl_porcentaje = 0.02
    if tipo_operacion == "LONG":
        precio_entrada = precio_actual
        stop_loss = precio_entrada * (1 - sl_porcentaje)
        take_profit = precio_entrada + ancho_canal 
    else:
        precio_entrada = precio_actual
        stop_loss = resistencia * (1 + sl_porcentaje)
        take_profit = precio_entrada - ancho_canal
    riesgo = abs(precio_entrada - stop_loss)
    beneficio = abs(take_profit - precio_entrada)
    ratio_rr = beneficio / riesgo if riesgo > 0 else 0
    if ratio_rr < self.config.get('min_rr_ratio', 1.2):
        if tipo_operacion == "LONG":
            take_profit = precio_entrada + (riesgo * self.config['min_rr_ratio'])
        else:
            take_profit = precio_entrada - (riesgo * self.config['min_rr_ratio'])
    return precio_entrada, take_profit, stop_loss

def escanear_mercado(self):
    """Escanea el mercado con estrategia Breakout + Reentry - LÓGICA ORIGINAL INTACTA"""
    logger.info(f"\n🔍 Escaneando {len(self.config.get('symbols', []))} símbolos (Estrategia: Breakout + Reentry)...")
    senales_encontradas = 0
    for simbolo in self.config.get('symbols', []):
        try:
            if simbolo in self.operaciones_activas:
                logger.info(f"   ⚡ {simbolo} - Operación activa, omitiendo...")
                continue
            config_optima = self.buscar_configuracion_optima_simbolo(simbolo)
            if not config_optima:
                logger.info(f"   ❌ {simbolo} - No se encontró configuración válida")
                continue
            datos_mercado = self.obtener_datos_mercado_config(
                simbolo, config_optima['timeframe'], config_optima['num_velas']
            )
            if not datos_mercado:
                logger.info(f"   ❌ {simbolo} - Error obteniendo datos")
                continue
            info_canal = self.calcular_canal_regresion_config(datos_mercado, config_optima['num_velas'])
            if not info_canal:
                logger.info(f"   ❌ {simbolo} - Error calculando canal")
                continue
            estado_stoch = ""
            if info_canal['stoch_k'] <= 30:
                estado_stoch = "📉 OVERSOLD"
            elif info_canal['stoch_k'] >= 70:
                estado_stoch = "📈 OVERBOUGHT"
            else:
                estado_stoch = "➖ NEUTRO"
            precio_actual = datos_mercado['precio_actual']
            resistencia = info_canal['resistencia']
            soporte = info_canal['soporte']
            if precio_actual > resistencia:
                posicion = "🔼 FUERA (arriba)"
            elif precio_actual < soporte:
                posicion = "🔽 FUERA (abajo)"
            else:
                posicion = "📍 DENTRO"
            logger.info(
                f"📊 {simbolo} - {config_optima['timeframe']} - {config_optima['num_velas']}v | "
                f"{info_canal['direccion']} ({info_canal['angulo_tendencia']:.1f}° - {info_canal['fuerza_texto']}) | "
                f"Ancho: {info_canal['ancho_canal_porcentual']:.1f}% - Stoch: {info_canal['stoch_k']:.1f}/{info_canal['stoch_d']:.1f} {estado_stoch} | "
                f"Precio: {posicion}"
            )
            if (info_canal['nivel_fuerza'] < 2 or 
                abs(info_canal['coeficiente_pearson']) < 0.4 or 
                info_canal['r2_score'] < 0.4):
                continue
            if simbolo not in self.esperando_reentry:
                tipo_breakout = self.detectar_breakout(simbolo, info_canal, datos_mercado)
                if tipo_breakout:
                    self.esperando_reentry[simbolo] = {
                        'tipo': tipo_breakout,
                        'timestamp': datetime.now(),
                        'precio_breakout': precio_actual,
                        'config': config_optima
                    }
                    # Registrar el breakout detectado para evitar repeticiones
                    self.breakouts_detectados[simbolo] = {
                        'tipo': tipo_breakout,
                        'timestamp': datetime.now(),
                        'precio_breakout': precio_actual
                    }
                    logger.info(f"     🎯 {simbolo} - Breakout registrado, esperando reingreso...")
                    continue
            tipo_operacion = self.detectar_reentry(simbolo, info_canal, datos_mercado)
            if not tipo_operacion:
                continue
            precio_entrada, tp, sl = self.calcular_niveles_entrada(
                tipo_operacion, info_canal, datos_mercado['precio_actual']
            )
            if not precio_entrada or not tp or not sl:
                continue
            if simbolo in self.breakout_history:
                ultimo_breakout = self.breakout_history[simbolo]
                tiempo_desde_ultimo = (datetime.now() - ultimo_breakout).total_seconds() / 3600
                if tiempo_desde_ultimo < 2:
                    logger.info(f"   ⏳ {simbolo} - Señal reciente, omitiendo...")
                    continue
            breakout_info = self.esperando_reentry[simbolo]
            self.generar_senal_operacion(
                simbolo, tipo_operacion, precio_entrada, tp, sl, 
                info_canal, datos_mercado, config_optima, breakout_info
            )
            senales_encontradas += 1
            self.breakout_history[simbolo] = datetime.now()
            del self.esperando_reentry[simbolo]
        except Exception as e:
            logger.warning(f"⚠️ Error analizando {simbolo}: {e}")
            continue
    if self.esperando_reentry:
        logger.info(f"\n⏳ Esperando reingreso en {len(self.esperando_reentry)} símbolos:")
        for simbolo, info in self.esperando_reentry.items():
            tiempo_espera = (datetime.now() - info['timestamp']).total_seconds() / 60
            logger.info(f"   • {simbolo} - {info['tipo']} - Esperando {tiempo_espera:.1f} min")
    if self.breakouts_detectados:
        logger.info(f"\n⏰ Breakouts detectados recientemente:")
        for simbolo, info in self.breakouts_detectados.items():
            tiempo_desde_deteccion = (datetime.now() - info['timestamp']).total_seconds() / 60
            logger.info(f"   • {simbolo} - {info['tipo']} - Hace {tiempo_desde_deteccion:.1f} min")
    if senales_encontradas > 0:
        logger.info(f"✅ Se encontraron {senales_encontradas} señales de trading")
    else:
        logger.info("❌ No se encontraron señales en este ciclo")
    return senales_encontradas

# Métodos de gestión de operaciones
def verificar_cierre_operaciones(self):
    """Verifica cierre de operaciones - LÓGICA ORIGINAL INTACTA"""
    if not self.operaciones_activas:
        return []
    operaciones_cerradas = []
    for simbolo, operacion in list(self.operaciones_activas.items()):
        config_optima = self.config_optima_por_simbolo.get(simbolo)
        if not config_optima:
            continue
        datos = self.obtener_datos_mercado_config(simbolo, config_optima['timeframe'], config_optima['num_velas'])
        if not datos:
            continue
        precio_actual = datos['precio_actual']
        tp = operacion['take_profit']
        sl = operacion['stop_loss']
        tipo = operacion['tipo']
        resultado = None
        if tipo == "LONG":
            if precio_actual >= tp:
                resultado = "TP"
            elif precio_actual <= sl:
                resultado = "SL"
        else:
            if precio_actual <= tp:
                resultado = "TP"
            elif precio_actual >= sl:
                resultado = "SL"
        if resultado:
            if tipo == "LONG":
                pnl_percent = ((precio_actual - operacion['precio_entrada']) / operacion['precio_entrada']) * 100
            else:
                pnl_percent = ((operacion['precio_entrada'] - precio_actual) / operacion['precio_entrada']) * 100
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
            self.registrar_operacion(datos_operacion)
            operaciones_cerradas.append(simbolo)
            del self.operaciones_activas[simbolo]
            if simbolo in self.senales_enviadas:
                self.senales_enviadas.remove(simbolo)
            self.operaciones_desde_optimizacion += 1
            logger.info(f"     📊 {simbolo} Operación {resultado} - PnL: {pnl_percent:.2f}%")
    return operaciones_cerradas

def inicializar_log(self):
    """Inicializa archivo de log - LÓGICA ORIGINAL INTACTA"""
    if not os.path.exists(self.archivo_log):
        with open(self.archivo_log, 'w', newline='', encoding='utf-8') as f:
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

def registrar_operacion(self, datos_operacion):
    """Registra operación en CSV - LÓGICA ORIGINAL INTACTA"""
    with open(self.archivo_log, 'a', newline='', encoding='utf-8') as f:
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

def ejecutar_analisis(self):
    """Ejecuta análisis completo - LÓGICA ORIGINAL INTACTA"""
    if random.random() < 0.1:
        self.reoptimizar_periodicamente()
        self.verificar_envio_reporte_automatico()    
    cierres = self.verificar_cierre_operaciones()
    if cierres:
        logger.info(f"     📊 Operaciones cerradas: {', '.join(cierres)}")
    self.guardar_estado()
    return self.escanear_mercado()