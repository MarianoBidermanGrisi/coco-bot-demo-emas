"""
Cliente para la API de Binance
Maneja todas las conexiones con la API de Binance con manejo de errores robusto
"""

import requests
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from ..config.settings import *

logger = logging.getLogger(__name__)

class BinanceClient:
    """Cliente para la API de Binance con manejo robusto de errores"""
    
    def __init__(self):
        """Inicializa el cliente de Binance"""
        self.base_url = BINANCE_BASE_URL
        self.timeout = API_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY
        
        # Configurar sesión con reintentos
        self.session = self._create_session()
        
        # Métricas de conexión
        self.request_count = 0
        self.error_count = 0
        self.last_request_time = 0
        
        logger.info(f"✅ Cliente Binance inicializado - URL: {self.base_url}")
    
    def _create_session(self) -> requests.Session:
        """Crea una sesión configurada con reintentos"""
        try:
            session = requests.Session()
            
            # Configurar reintentos automáticos
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Headers por defecto
            session.headers.update({
                'User-Agent': 'TradingBot/1.0',
                'Content-Type': 'application/json'
            })
            
            logger.debug("✅ Sesión HTTP configurada con reintentos")
            return session
            
        except Exception as e:
            logger.error(f"❌ Error creando sesión HTTP: {e}")
            raise
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Realiza una request con manejo de errores robusto"""
        try:
            # Rate limiting básico
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < 0.1:  # Mínimo 100ms entre requests
                time.sleep(0.1 - time_since_last)
            
            self.last_request_time = time.time()
            self.request_count += 1
            
            url = f"{self.base_url}{endpoint}"
            params = kwargs.get('params', {})
            data = kwargs.get('data', {})
            
            logger.debug(f"🔄 {method} {endpoint} - Params: {params}")
            
            # Realizar request
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            # Verificar status code
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.debug(f"✅ Request exitosa - Response: {result}")
                    return result
                except Exception as e:
                    logger.error(f"❌ Error parseando JSON: {e}")
                    self.error_count += 1
                    return None
                    
            elif response.status_code == 429:
                logger.warning(f"⚠️ Rate limit excedido - Esperando {self.retry_delay}s")
                time.sleep(self.retry_delay)
                return self._make_request(method, endpoint, **kwargs)
                
            elif response.status_code >= 500:
                logger.error(f"❌ Error del servidor {response.status_code} - {response.text}")
                self.error_count += 1
                return None
                
            else:
                logger.error(f"❌ Error HTTP {response.status_code} - {response.text}")
                self.error_count += 1
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout en request a {endpoint}")
            self.error_count += 1
            return None
            
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Error de conexión a {endpoint}")
            self.error_count += 1
            return None
            
        except Exception as e:
            logger.error(f"❌ Error inesperado en request a {endpoint}: {e}")
            self.error_count += 1
            return None
    
    def get_server_time(self) -> Optional[Dict]:
        """Obtiene el tiempo del servidor de Binance"""
        try:
            return self._make_request('GET', '/api/v3/time')
        except Exception as e:
            logger.error(f"❌ Error obteniendo tiempo del servidor: {e}")
            return None
    
    def get_exchange_info(self) -> Optional[Dict]:
        """Obtiene información del exchange"""
        try:
            return self._make_request('GET', '/api/v3/exchangeInfo')
        except Exception as e:
            logger.error(f"❌ Error obteniendo info del exchange: {e}")
            return None
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Obtiene el precio actual de un símbolo"""
        try:
            params = {'symbol': symbol}
            result = self._make_request('GET', '/api/v3/ticker/price', params=params)
            
            if result and 'price' in result:
                return float(result['price'])
            else:
                logger.warning(f"⚠️ No se pudo obtener precio para {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo precio de {symbol}: {e}")
            return None
    
    def get_24hr_ticker(self, symbol: str) -> Optional[Dict]:
        """Obtiene estadísticas de 24 horas para un símbolo"""
        try:
            params = {'symbol': symbol}
            result = self._make_request('GET', '/api/v3/ticker/24hr', params=params)
            return result
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo ticker 24h para {symbol}: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Prueba la conexión con Binance"""
        try:
            logger.info("🔍 Probando conexión con Binance...")
            
            # Verificar tiempo del servidor
            server_time = self.get_server_time()
            if not server_time:
                logger.error("❌ No se pudo obtener tiempo del servidor")
                return False
            
            # Verificar exchange info
            exchange_info = self.get_exchange_info()
            if not exchange_info:
                logger.error("❌ No se pudo obtener info del exchange")
                return False
            
            # Verificar un símbolo específico
            btc_price = self.get_ticker_price('BTCUSDT')
            if not btc_price:
                logger.error("❌ No se pudo obtener precio de BTCUSDT")
                return False
            
            logger.info(f"✅ Conexión exitosa - BTC Price: ${btc_price:,.2f}")
            logger.info(f"📊 Request count: {self.request_count}, Errors: {self.error_count}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error probando conexión: {e}")
            return False
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de conexión"""
        return {
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': (self.error_count / max(self.request_count, 1)) * 100,
            'last_request_time': self.last_request_time,
            'base_url': self.base_url,
            'timeout': self.timeout
        }
    
    def close(self):
        """Cierra la sesión"""
        try:
            if hasattr(self, 'session'):
                self.session.close()
            logger.info("✅ Sesión de Binance cerrada")
        except Exception as e:
            logger.error(f"❌ Error cerrando sesión: {e}")

# Instancia global del cliente
binance_client = BinanceClient()

def get_binance_client() -> BinanceClient:
    """Obtiene la instancia global del cliente de Binance"""
    return binance_client
