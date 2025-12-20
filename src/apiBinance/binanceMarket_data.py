"""
Gestor de Datos de Mercado
Maneja la obtención y procesamiento de datos de mercado desde Binance
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .binance_client import get_binance_client
from ..config.settings import *

logger = logging.getLogger(__name__)

class MarketDataManager:
    """Gestor de datos de mercado con manejo robusto de errores"""
    
    def __init__(self):
        """Inicializa el gestor de datos de mercado"""
        self.client = get_binance_client()
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 30  # segundos
        
        logger.info("📊 MarketDataManager inicializado")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica si el cache es válido"""
        if cache_key not in self.cache_expiry:
            return False
        
        expiry_time = self.cache_expiry[cache_key]
        return datetime.now() < expiry_time
    
    def _update_cache(self, cache_key: str, data: Any) -> None:
        """Actualiza el cache con nuevos datos"""
        self.cache[cache_key] = data
        self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
    
    def get_klines(self, symbol: str, interval: str, limit: int = 500) -> Optional[List]:
        """
        Obtiene datos de klines (candlesticks) desde Binance
        
        Args:
            symbol: Símbolo de trading (ej: BTCUSDT)
            interval: Intervalo de tiempo (ej: 1m, 5m, 1h)
            limit: Número de velas a obtener
            
        Returns:
            Lista de klines o None si hay error
        """
        try:
            cache_key = f"klines_{symbol}_{interval}_{limit}"
            
            # Verificar cache
            if self._is_cache_valid(cache_key) and cache_key in self.cache:
                logger.debug(f"📦 Datos desde cache: {symbol} {interval}")
                return self.cache[cache_key]
            
            # Realizar request
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': min(limit, 1000)  # Binance tiene límite de 1000
            }
            
            logger.debug(f"🔄 Obteniendo klines: {symbol} {interval} ({limit})")
            
            result = self.client._make_request('GET', '/api/v3/klines', params=params)
            
            if result and isinstance(result, list) and len(result) > 0:
                self._update_cache(cache_key, result)
                logger.debug(f"✅ Klines obtenidos: {len(result)} velas")
                return result
            else:
                logger.warning(f"⚠️ No se pudieron obtener klines para {symbol} {interval}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo klines {symbol} {interval}: {e}")
            return None
    
    def get_market_data(self, symbol: str, timeframe: str, num_velas: int) -> Optional[Dict]:
        """
        Obtiene datos de mercado procesados para análisis
        
        Args:
            symbol: Símbolo de trading
            timeframe: Timeframe (ej: 1m, 5m)
            num_velas: Número de velas a analizar
            
        Returns:
            Dict con datos procesados o None si hay error
        """
        try:
            # Obtener klines
            klines = self.get_klines(symbol, timeframe, num_velas + 14)
            if not klines or len(klines) < num_velas:
                logger.warning(f"⚠️ Insuficientes klines para {symbol} {timeframe}")
                return None
            
            # Procesar datos
            datos = self._process_klines(klines, num_velas)
            
            if datos:
                logger.debug(f"✅ Datos procesados para {symbol} {timeframe}")
                return datos
            else:
                logger.warning(f"⚠️ Error procesando datos para {symbol} {timeframe}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos de mercado {symbol}: {e}")
            return None
    
    def _process_klines(self, klines: List, num_velas: int) -> Optional[Dict]:
        """
        Procesa klines en formato para análisis
        
        Args:
            klines: Lista de klines desde Binance
            num_velas: Número de velas a procesar
            
        Returns:
            Dict con datos procesados
        """
        try:
            if not klines or len(klines) < num_velas:
                return None
            
            # Tomar las últimas velas
            klines_to_process = klines[-num_velas:]
            
            # Extraer datos OHLCV
            maximos = []
            minimos = []
            cierres = []
            tiempos = []
            
            for i, kline in enumerate(klines_to_process):
                try:
                    # kline format: [open_time, open_price, high_price, low_price, close_price, volume, ...]
                    open_price = float(kline[1])
                    high_price = float(kline[2])
                    low_price = float(kline[3])
                    close_price = float(kline[4])
                    
                    maximos.append(high_price)
                    minimos.append(low_price)
                    cierres.append(close_price)
                    tiempos.append(i)
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"⚠️ Error procesando kline: {e}")
                    continue
            
            if len(maximos) < num_velas or len(minimos) < num_velas or len(cierres) < num_velas:
                logger.warning(f"⚠️ Datos insuficientes después del procesamiento")
                return None
            
            precio_actual = cierres[-1] if cierres else 0
            
            return {
                'maximos': maximos,
                'minimos': minimos,
                'cierres': cierres,
                'tiempos': tiempos,
                'precio_actual': precio_actual,
                'timeframe': None,  # Se asignará después
                'num_velas': len(cierres),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando klines: {e}")
            return None
    
    def validate_symbol(self, symbol: str) -> bool:
        """Valida si un símbolo es válido"""
        try:
            # Intentar obtener el precio actual
            price = self.client.get_ticker_price(symbol)
            return price is not None
            
        except Exception as e:
            logger.warning(f"⚠️ Error validando símbolo {symbol}: {e}")
            return False
    
    def get_multiple_market_data(self, symbols: List[str], timeframe: str, num_velas: int) -> Dict[str, Optional[Dict]]:
        """
        Obtiene datos de mercado para múltiples símbolos
        
        Args:
            symbols: Lista de símbolos
            timeframe: Timeframe
            num_velas: Número de velas
            
        Returns:
            Dict con datos por símbolo
        """
        try:
            logger.info(f"🔄 Obteniendo datos para {len(symbols)} símbolos ({timeframe})")
            
            results = {}
            for symbol in symbols:
                try:
                    datos = self.get_market_data(symbol, timeframe, num_velas)
                    results[symbol] = datos
                    
                    # Pequeña pausa para no sobrecargar la API
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error obteniendo datos para {symbol}: {e}")
                    results[symbol] = None
            
            successful = sum(1 for v in results.values() if v is not None)
            logger.info(f"✅ Datos obtenidos para {successful}/{len(symbols)} símbolos")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos múltiples: {e}")
            return {symbol: None for symbol in symbols}
    
    def clear_cache(self) -> None:
        """Limpia el cache de datos"""
        try:
            self.cache.clear()
            self.cache_expiry.clear()
            logger.info("🗑️ Cache de datos limpiado")
        except Exception as e:
            logger.error(f"❌ Error limpiando cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        try:
            current_time = datetime.now()
            valid_entries = sum(1 for expiry in self.cache_expiry.values() if expiry > current_time)
            
            return {
                'total_entries': len(self.cache),
                'valid_entries': valid_entries,
                'expired_entries': len(self.cache) - valid_entries,
                'cache_duration_seconds': self.cache_duration
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas del cache: {e}")
            return {}

# Instancia global del gestor de datos de mercado
market_data_manager = MarketDataManager()

def get_market_data_manager() -> MarketDataManager:
    """Obtiene la instancia global del gestor de datos de mercado"""
    return market_data_manager
