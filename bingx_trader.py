# bingx_trader.py
import requests
import time
import json
import hashlib
import hmac
import logging
import math
from urllib.parse import urlencode
from datetime import datetime

logger_bingx = logging.getLogger("BingXTrader")

class BingXTrader:
    def __init__(self, api_key, secret_key, testnet=False):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://open-api.bingx.com"
        self.testnet = testnet
        
        if testnet:
            logger_bingx.info("🧪 BingXTrader inicializado en MODO TESTNET.")
        else:
            logger_bingx.warning("🚨 BingXTrader inicializado en MODO REAL. 🚨")

    def _generate_signature(self, params):
        """Genera firma HMAC-SHA256 para BingX"""
        query_string = urlencode(params)
        return hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _request(self, endpoint, params=None, method='GET', signed=False):
        """Método genérico para requests a BingX API"""
        url = f"{self.base_url}{endpoint}"
        
        if signed:
            if params is None:
                params = {}
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        headers = {
            'X-BX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=10)
            else:
                response = requests.post(url, json=params, headers=headers, timeout=10)
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') != 0:
                logger_bingx.error(f"❌ Error BingX API: {data}")
                return None
                
            return data.get('data')
            
        except Exception as e:
            logger_bingx.error(f"❌ Error en request BingX: {e}")
            return None

    def check_connection(self):
        """Verificar conexión con BingX"""
        try:
            result = self.get_account_info()
            if result:
                logger_bingx.info("✅ Conexión con BingX exitosa.")
                return True
            return False
        except Exception as e:
            logger_bingx.error(f"❌ Error al conectar con BingX: {e}")
            return False

    def set_leverage(self, symbol, leverage):
        """Establecer apalancamiento en BingX"""
        try:
            endpoint = "/openApi/swap/v2/trade/leverage"
            params = {
                'symbol': self._format_symbol(symbol),
                'leverage': leverage,
                'side': 1  # Both sides
            }
            
            result = self._request(endpoint, params, 'POST', True)
            if result:
                logger_bingx.info(f"✅ Apalancamiento {leverage}x establecido para {symbol}.")
                return True
            return False
        except Exception as e:
            logger_bingx.error(f"❌ Error al establecer apalancamiento: {e}")
            return False

    def _format_symbol(self, symbol):
        """Formatear símbolo para BingX (BTCUSDT -> BTC-USDT)"""
        return symbol.replace('USDT', '-USDT')

    def get_account_info(self):
        """Obtener información de la cuenta"""
        endpoint = "/openApi/swap/v2/user/balance"
        return self._request(endpoint, {}, 'GET', True)

    def get_symbol_info(self, symbol):
        """Obtener información del símbolo"""
        endpoint = "/openApi/swap/v2/quote/contracts"
        result = self._request(endpoint, {}, 'GET', False)
        
        if result:
            bingx_symbol = self._format_symbol(symbol)
            for contract in result:
                if contract['symbol'] == bingx_symbol:
                    return contract
        return None

    def get_price_precision(self, symbol):
        """Obtener precisión de precio"""
        symbol_info = self.get_symbol_info(symbol)
        if symbol_info and 'pricePrecision' in symbol_info:
            return symbol_info['pricePrecision']
        return 8

    def get_quantity_precision(self, symbol):
        """Obtener precisión de cantidad"""
        symbol_info = self.get_symbol_info(symbol)
        if symbol_info and 'quantityPrecision' in symbol_info:
            return symbol_info['quantityPrecision']
        return 8

    def get_current_price(self, symbol):
        """Obtener precio actual"""
        try:
            endpoint = "/openApi/swap/v2/quote/ticker"
            params = {'symbol': self._format_symbol(symbol)}
            result = self._request(endpoint, params, 'GET', False)
            
            if result and len(result) > 0:
                return float(result[0]['lastPrice'])
            return None
        except Exception as e:
            logger_bingx.error(f"❌ Error obteniendo precio de {symbol}: {e}")
            return None

    def place_market_order(self, symbol, side, quantity):
        """Colocar orden de mercado"""
        try:
            bingx_symbol = self._format_symbol(symbol)
            
            endpoint = "/openApi/swap/v2/trade/order"
            params = {
                'symbol': bingx_symbol,
                'side': side.upper(),
                'type': 'MARKET',
                'quantity': quantity,
                'positionSide': 'LONG' if side.upper() == 'BUY' else 'SHORT'
            }
            
            result = self._request(endpoint, params, 'POST', True)
            if result:
                logger_bingx.info(f"✅ Orden MARKET ejecutada: {side} {quantity} {symbol}")
                return result
            return None
        except Exception as e:
            logger_bingx.error(f"❌ Error al colocar orden: {e}")
            return None

    def place_stop_loss_order(self, symbol, side, stop_price):
        """Colocar orden Stop Loss"""
        try:
            bingx_symbol = self._format_symbol(symbol)
            
            endpoint = "/openApi/swap/v2/trade/order"
            params = {
                'symbol': bingx_symbol,
                'side': 'SELL' if side.upper() == 'BUY' else 'BUY',
                'type': 'STOP_MARKET',
                'stopPrice': stop_price,
                'closePosition': 'true',
                'positionSide': 'LONG' if side.upper() == 'BUY' else 'SHORT'
            }
            
            result = self._request(endpoint, params, 'POST', True)
            if result:
                logger_bingx.info(f"✅ Stop-Loss colocado en {stop_price} para {symbol}")
                return result
            return None
        except Exception as e:
            logger_bingx.error(f"❌ Error al colocar Stop-Loss: {e}")
            return None

    def place_take_profit_order(self, symbol, side, take_profit_price):
        """Colocar orden Take Profit"""
        try:
            bingx_symbol = self._format_symbol(symbol)
            
            endpoint = "/openApi/swap/v2/trade/order"
            params = {
                'symbol': bingx_symbol,
                'side': 'SELL' if side.upper() == 'BUY' else 'BUY',
                'type': 'TAKE_PROFIT_MARKET',
                'stopPrice': take_profit_price,
                'closePosition': 'true',
                'positionSide': 'LONG' if side.upper() == 'BUY' else 'SHORT'
            }
            
            result = self._request(endpoint, params, 'POST', True)
            if result:
                logger_bingx.info(f"✅ Take-Profit colocado en {take_profit_price} para {symbol}")
                return result
            return None
        except Exception as e:
            logger_bingx.error(f"❌ Error al colocar Take-Profit: {e}")
            return None

    def get_open_positions(self, symbol=None):
        """Obtener posiciones abiertas"""
        endpoint = "/openApi/swap/v2/user/positions"
        result = self._request(endpoint, {}, 'GET', True)
        
        if result:
            if symbol:
                bingx_symbol = self._format_symbol(symbol)
                return [pos for pos in result if pos['symbol'] == bingx_symbol]
            return result
        return []

    def get_open_orders(self, symbol=None):
        """Obtener órdenes abiertas"""
        endpoint = "/openApi/swap/v2/trade/openOrders"
        params = {}
        if symbol:
            params['symbol'] = self._format_symbol(symbol)
            
        return self._request(endpoint, params, 'GET', True) or []

    def cancel_order(self, symbol, order_id):
        """Cancelar orden específica"""
        endpoint = "/openApi/swap/v2/trade/cancel"
        params = {
            'symbol': self._format_symbol(symbol),
            'orderId': order_id
        }
        
        return self._request(endpoint, params, 'POST', True)

    def validar_niveles_sl_tp(self, symbol, side, sl_price, tp_price):
        """Validar niveles SL/TP"""
        try:
            precio_actual = self.get_current_price(symbol)
            if not precio_actual:
                return sl_price, tp_price
            
            # Misma lógica de validación que en Binance
            tick_size = 0.0001
            min_distance = tick_size * 10
            
            if side.upper() == 'BUY':  # SHORT → SL arriba, TP abajo
                if sl_price <= precio_actual + min_distance:
                    sl_price = precio_actual * 1.008
                if tp_price >= precio_actual - min_distance:
                    tp_price = precio_actual * 0.992
            else:  # LONG → SL abajo, TP arriba
                if sl_price >= precio_actual - min_distance:
                    sl_price = precio_actual * 0.992
                if tp_price <= precio_actual + min_distance:
                    tp_price = precio_actual * 1.008
            
            # Asegurar que SL y TP no estén demasiado cerca entre sí
            distance_sl_tp = abs(sl_price - tp_price)
            if distance_sl_tp < (min_distance * 5):
                if side.upper() == 'BUY':
                    tp_price = sl_price - (min_distance * 10)
                else:
                    tp_price = sl_price + (min_distance * 10)
                    
            logger_bingx.info(f"✅ Niveles validados BingX: SL={sl_price:.8f}, TP={tp_price:.8f}, Precio={precio_actual:.8f}")
            return sl_price, tp_price
            
        except Exception as e:
            logger_bingx.error(f"❌ Error validando SL/TP BingX: {e}")
            return sl_price, tp_price

    def verificar_distancia_ordenes(self, symbol, precio_actual, sl_price, tp_price, side):
        """Verificar distancia de órdenes"""
        try:
            symbol_info = self.get_symbol_info(symbol)
            min_price_distance = 0.0001
            
            if symbol_info and 'pricePrecision' in symbol_info:
                tick_size = 1.0 / (10 ** symbol_info['pricePrecision'])
                min_price_distance = tick_size * 15
            
            # Verificar distancia del SL
            distancia_sl = abs(precio_actual - sl_price)
            if distancia_sl < min_price_distance:
                if side.upper() == 'BUY':  # SHORT
                    sl_price = precio_actual * 1.01
                else:  # LONG
                    sl_price = precio_actual * 0.99
                logger_bingx.warning(f"⚠️ SL ajustado por distancia insuficiente: {sl_price:.8f}")
            
            # Verificar distancia del TP
            distancia_tp = abs(precio_actual - tp_price)
            if distancia_tp < min_price_distance:
                if side.upper() == 'BUY':  # SHORT
                    tp_price = precio_actual * 0.99
                else:  # LONG
                    tp_price = precio_actual * 1.01
                logger_bingx.warning(f"⚠️ TP ajustado por distancia insuficiente: {tp_price:.8f}")
            
            return sl_price, tp_price
            
        except Exception as e:
            logger_bingx.error(f"❌ Error verificando distancia órdenes: {e}")
            return sl_price, tp_price

    def cancelar_ordenes_cierre(self, symbol):
        """Cancelar órdenes de cierre"""
        try:
            open_orders = self.get_open_orders(symbol)
            for order in open_orders:
                if order['type'] in ['STOP_MARKET', 'TAKE_PROFIT_MARKET']:
                    self.cancel_order(symbol, order['orderId'])
                    logger_bingx.info(f"🧹 Orden cancelada BingX: {order['type']} ID {order['orderId']}")
        except Exception as e:
            logger_bingx.error(f"❌ Error al cancelar órdenes BingX: {e}")

    def verificar_ordenes_cierre_activas(self, symbol):
        """Verificar órdenes activas"""
        try:
            open_orders = self.get_open_orders(symbol)
            sl_active = any(order['type'] == 'STOP_MARKET' for order in open_orders)
            tp_active = any(order['type'] == 'TAKE_PROFIT_MARKET' for order in open_orders)
            
            logger_bingx.info(f"🔍 Verificando órdenes BingX {symbol}: SL={sl_active}, TP={tp_active}")
            return sl_active, tp_active
        except Exception as e:
            logger_bingx.error(f"❌ Error verificando órdenes BingX: {e}")
            return False, False

    def recolocar_ordenes_cierre(self, symbol, side, sl_price, tp_price):
        """Re-colocar órdenes de cierre"""
        try:
            sl_active, tp_active = self.verificar_ordenes_cierre_activas(symbol)
            
            if not sl_active:
                logger_bingx.warning(f"⚠️ Stop Loss no encontrado en BingX {symbol}, recolocando...")
                sl_order = self.place_stop_loss_order(symbol, side, sl_price)
                if not sl_order:
                    logger_bingx.error(f"❌ Error crítico: No se pudo recolocar SL en {symbol}")
                    return False
            
            if not tp_active:
                logger_bingx.warning(f"⚠️ Take Profit no encontrado en BingX {symbol}, recolocando...")
                tp_order = self.place_take_profit_order(symbol, side, tp_price)
                if not tp_order:
                    logger_bingx.error(f"❌ Error crítico: No se pudo recolocar TP en {symbol}")
                    return False
            
            return True
        except Exception as e:
            logger_bingx.error(f"❌ Error recolocando órdenes BingX: {e}")
            return False