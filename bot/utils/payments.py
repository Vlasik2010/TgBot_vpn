"""Payment processing utilities for VPN Bot"""

import logging
import hashlib
import hmac
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from urllib.parse import urlencode

from bot.config.settings import Config

logger = logging.getLogger(__name__)


class PaymentError(Exception):
    """Custom payment processing error"""
    pass


class YooMoneyPayment:
    """YooMoney payment processor"""
    
    def __init__(self):
        self.token = Config.YOOMONEY_TOKEN
        self.base_url = "https://yoomoney.ru/api"
    
    def create_payment(self, amount: int, order_id: str, description: str) -> Dict[str, Any]:
        """Create YooMoney payment"""
        try:
            url = f"{self.base_url}/request-payment"
            data = {
                'pattern_id': 'p2p',
                'to': self.token,
                'amount': amount / 100,  # Convert kopecks to rubles
                'comment': description,
                'message': description,
                'label': order_id
            }
            
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(url, data=data, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('status') == 'success':
                return {
                    'payment_id': result.get('request_id'),
                    'payment_url': f"https://yoomoney.ru/checkout/payments/v2/contract?request_id={result.get('request_id')}",
                    'amount': amount,
                    'expires_at': datetime.utcnow() + timedelta(minutes=15)
                }
            else:
                raise PaymentError(f"YooMoney error: {result.get('error')}")
                
        except requests.RequestException as e:
            logger.error(f"YooMoney API error: {e}")
            raise PaymentError("Ошибка подключения к YooMoney")
        except Exception as e:
            logger.error(f"YooMoney payment creation error: {e}")
            raise PaymentError("Ошибка создания платежа YooMoney")
    
    def check_payment(self, payment_id: str) -> str:
        """Check YooMoney payment status"""
        try:
            url = f"{self.base_url}/operation-details"
            data = {'operation_id': payment_id}
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(url, data=data, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            status = result.get('status', 'unknown')
            
            if status == 'success':
                return 'completed'
            elif status in ['refused', 'failed']:
                return 'failed'
            else:
                return 'pending'
                
        except Exception as e:
            logger.error(f"YooMoney payment check error: {e}")
            return 'unknown'


class QiwiPayment:
    """QIWI payment processor"""
    
    def __init__(self):
        self.token = Config.QIWI_TOKEN
        self.base_url = "https://api.qiwi.com"
    
    def create_payment(self, amount: int, order_id: str, description: str) -> Dict[str, Any]:
        """Create QIWI payment"""
        try:
            url = f"{self.base_url}/partner/bill/v1/bills/{order_id}"
            
            data = {
                'amount': {
                    'currency': 'RUB',
                    'value': f"{amount / 100:.2f}"
                },
                'comment': description,
                'expirationDateTime': (datetime.utcnow() + timedelta(minutes=15)).isoformat() + 'Z',
                'customer': {},
                'customFields': {}
            }
            
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.put(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            return {
                'payment_id': result['billId'],
                'payment_url': result['payUrl'],
                'amount': amount,
                'expires_at': datetime.utcnow() + timedelta(minutes=15)
            }
            
        except requests.RequestException as e:
            logger.error(f"QIWI API error: {e}")
            raise PaymentError("Ошибка подключения к QIWI")
        except Exception as e:
            logger.error(f"QIWI payment creation error: {e}")
            raise PaymentError("Ошибка создания платежа QIWI")
    
    def check_payment(self, payment_id: str) -> str:
        """Check QIWI payment status"""
        try:
            url = f"{self.base_url}/partner/bill/v1/bills/{payment_id}"
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            status = result.get('status', {}).get('value', 'unknown')
            
            if status == 'PAID':
                return 'completed'
            elif status in ['REJECTED', 'EXPIRED']:
                return 'failed'
            else:
                return 'pending'
                
        except Exception as e:
            logger.error(f"QIWI payment check error: {e}")
            return 'unknown'


class CryptomusPayment:
    """Cryptomus cryptocurrency payment processor"""
    
    def __init__(self):
        self.api_key = Config.CRYPTOMUS_API_KEY
        self.merchant_id = Config.CRYPTOMUS_MERCHANT_ID
        self.base_url = "https://api.cryptomus.com/v1"
    
    def _generate_signature(self, data: dict) -> str:
        """Generate signature for Cryptomus API"""
        json_data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        encoded_data = json_data.encode('utf-8')
        signature = hmac.new(
            self.api_key.encode('utf-8'),
            encoded_data,
            hashlib.md5
        ).hexdigest()
        return signature
    
    def create_payment(self, amount: int, order_id: str, description: str) -> Dict[str, Any]:
        """Create cryptocurrency payment"""
        try:
            url = f"{self.base_url}/payment"
            
            data = {
                'amount': str(amount / 100),  # Convert to rubles
                'currency': 'RUB',
                'order_id': order_id,
                'merchant': self.merchant_id,
                'url_callback': 'https://your-domain.com/webhook/cryptomus',
                'url_return': 'https://t.me/your_bot',
                'url_success': 'https://t.me/your_bot',
                'is_payment_multiple': False,
                'lifetime': 900,  # 15 minutes
                'to_currency': 'USDT'  # Default to USDT
            }
            
            headers = {
                'merchant': self.merchant_id,
                'sign': self._generate_signature(data),
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('state') == 0:  # Success
                payment_data = result.get('result', {})
                return {
                    'payment_id': payment_data.get('uuid'),
                    'payment_url': payment_data.get('url'),
                    'amount': amount,
                    'expires_at': datetime.utcnow() + timedelta(minutes=15)
                }
            else:
                raise PaymentError(f"Cryptomus error: {result.get('message')}")
                
        except requests.RequestException as e:
            logger.error(f"Cryptomus API error: {e}")
            raise PaymentError("Ошибка подключения к Cryptomus")
        except Exception as e:
            logger.error(f"Cryptomus payment creation error: {e}")
            raise PaymentError("Ошибка создания криптоплатежа")
    
    def check_payment(self, payment_id: str) -> str:
        """Check cryptocurrency payment status"""
        try:
            url = f"{self.base_url}/payment/info"
            data = {
                'merchant': self.merchant_id,
                'uuid': payment_id
            }
            
            headers = {
                'merchant': self.merchant_id,
                'sign': self._generate_signature(data),
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('state') == 0:
                payment_data = result.get('result', {})
                status = payment_data.get('payment_status')
                
                if status == 'paid':
                    return 'completed'
                elif status in ['fail', 'cancel', 'system_fail']:
                    return 'failed'
                else:
                    return 'pending'
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Cryptomus payment check error: {e}")
            return 'unknown'


class PaymentManager:
    """Main payment manager class"""
    
    def __init__(self):
        self.yoomoney = YooMoneyPayment() if Config.YOOMONEY_TOKEN else None
        self.qiwi = QiwiPayment() if Config.QIWI_TOKEN else None
        self.cryptomus = CryptomusPayment() if Config.CRYPTOMUS_API_KEY else None
    
    def create_payment(self, method: str, amount: int, order_id: str, description: str) -> Dict[str, Any]:
        """Create payment with specified method"""
        try:
            if method == 'yoomoney' and self.yoomoney:
                return self.yoomoney.create_payment(amount, order_id, description)
            elif method == 'qiwi' and self.qiwi:
                return self.qiwi.create_payment(amount, order_id, description)
            elif method == 'crypto' and self.cryptomus:
                return self.cryptomus.create_payment(amount, order_id, description)
            else:
                raise PaymentError(f"Платежный метод {method} недоступен")
                
        except PaymentError:
            raise
        except Exception as e:
            logger.error(f"Payment creation error: {e}")
            raise PaymentError("Ошибка создания платежа")
    
    def check_payment(self, method: str, payment_id: str) -> str:
        """Check payment status"""
        try:
            if method == 'yoomoney' and self.yoomoney:
                return self.yoomoney.check_payment(payment_id)
            elif method == 'qiwi' and self.qiwi:
                return self.qiwi.check_payment(payment_id)
            elif method == 'crypto' and self.cryptomus:
                return self.cryptomus.check_payment(payment_id)
            else:
                return 'unknown'
                
        except Exception as e:
            logger.error(f"Payment check error: {e}")
            return 'unknown'
    
    def get_available_methods(self) -> list:
        """Get list of available payment methods"""
        methods = []
        if self.yoomoney:
            methods.append('yoomoney')
        if self.qiwi:
            methods.append('qiwi')
        if self.cryptomus:
            methods.append('crypto')
        return methods


# Global payment manager instance
payment_manager = PaymentManager()