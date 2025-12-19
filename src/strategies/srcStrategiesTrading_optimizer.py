"""
Optimizador IA para el Bot de Trading
**REGLA DE ORO: NO MODIFICAR LA LÓGICA ORIGINAL**
Código copiado íntegramente del archivo original
"""

import csv
import os
import statistics
import math
import itertools
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class OptimizadorIA:
    """
    Optimizador IA - LÓGICA ORIGINAL INTACTA
    NO MODIFICAR ESTE CÓDIGO
    """
    def __init__(self, log_path="operaciones_log.csv", min_samples=15):
        try:
            self.log_path = log_path
            self.min_samples = min_samples
            self.datos = self.cargar_datos()
            logger.info(f"📊 OptimizadorIA inicializado - Min samples: {min_samples}")
        except Exception as e:
            logger.error(f"❌ Error inicializando OptimizadorIA: {e}")
            self.log_path = log_path
            self.min_samples = min_samples
            self.datos = []

    def cargar_datos(self):
        """Carga datos desde CSV - LÓGICA ORIGINAL"""
        datos = []
        try:
            if not os.path.exists(self.log_path):
                logger.warning(f"⚠️ No se encontró {self.log_path}")
                return datos
                
            with open(self.log_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        pnl = float(row.get('pnl_percent', 0))
                        angulo = float(row.get('angulo_tendencia', 0))
                        pearson = float(row.get('pearson', 0))
                        r2 = float(row.get('r2_score', 0))
                        ancho_relativo = float(row.get('ancho_canal_relativo', 0))
                        nivel_fuerza = int(row.get('nivel_fuerza', 1))
                        datos.append({
                            'pnl': pnl, 
                            'angulo': angulo, 
                            'pearson': pearson, 
                            'r2': r2,
                            'ancho_relativo': ancho_relativo,
                            'nivel_fuerza': nivel_fuerza
                        })
                    except Exception:
                        continue
            logger.info(f"✅ Datos cargados: {len(datos)} operaciones")
        except Exception as e:
            logger.error(f"❌ Error cargando datos: {e}")
        return datos

    def evaluar_configuracion(self, trend_threshold, min_strength, entry_margin):
        """Evalúa configuración - LÓGICA ORIGINAL INTACTA"""
        if not self.datos:
            return -99999
        filtradas = [
            op for op in self.datos
            if abs(op['angulo']) >= trend_threshold
            and abs(op['angulo']) >= min_strength
            and abs(op['pearson']) >= 0.4
            and op.get('nivel_fuerza', 1) >= 2
            and op.get('r2', 0) >= 0.4
        ]
        n = len(filtradas)
        if n < max(8, int(0.15 * len(self.datos))):
            return -10000 - n
        pnls = [op['pnl'] for op in filtradas]
        pnl_mean = statistics.mean(pnls) if filtradas else 0
        pnl_std = statistics.stdev(pnls) if len(pnls) > 1 else 0
        winrate = sum(1 for op in filtradas if op['pnl'] > 0) / n if n > 0 else 0
        score = (pnl_mean - 0.5 * pnl_std) * winrate * math.sqrt(n)
        ops_calidad = [op for op in filtradas if op.get('r2', 0) >= 0.6 and op.get('nivel_fuerza', 1) >= 3]
        if ops_calidad:
            score *= 1.2
        return score

    def buscar_mejores_parametros(self):
        """Busca mejores parámetros - LÓGICA ORIGINAL INTACTA"""
        if not self.datos or len(self.datos) < self.min_samples:
            logger.info(f"ℹ️ No hay suficientes datos para optimizar (se requieren {self.min_samples}, hay {len(self.datos)})")
            return None
        mejor_score = -1e9
        mejores_param = None
        trend_values = [3, 5, 8, 10, 12, 15, 18, 20, 25, 30, 35, 40]
        strength_values = [3, 5, 8, 10, 12, 15, 18, 20, 25, 30]
        margin_values = [0.0005, 0.001, 0.0015, 0.002, 0.0025, 0.003, 0.004, 0.005, 0.008, 0.01]
        combos = list(itertools.product(trend_values, strength_values, margin_values))
        total = len(combos)
        logger.info(f"🔎 Optimizador: probando {total} combinaciones...")
        for idx, (t, s, m) in enumerate(combos, start=1):
            score = self.evaluar_configuracion(t, s, m)
            if idx % 100 == 0 or idx == total:
                logger.info(f"   · probado {idx}/{total} combos (mejor score actual: {mejor_score:.4f})")
            if score > mejor_score:
                mejor_score = score = {
                    'trend_threshold_degrees
                mejores_param': t,
                    'min_trend_strength_degrees': s,
                    'entry_margin': m,
                    'score': score,
                    'evaluated_samples': len(self.datos),
                    'total_combinations': total
                }
        if mejores_param:
            logger.info(f"✅ Optimizador: mejores parámetros encontrados: {mejores_param}")
            try:
                with open("mejores_parametros.json", "w", encoding='utf-8') as f:
                    json.dump(mejores_param, f, indent=2)
                logger.info("✅ Parámetros guardados en mejores_parametros.json")
            except Exception as e:
                logger.warning(f"⚠️ Error guardando mejores_parametros.json: {e}")
        else:
            logger.warning("⚠️ No se encontró una configuración mejor")
        return mejores_param