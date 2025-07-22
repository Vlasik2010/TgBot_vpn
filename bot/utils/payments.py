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


# ====== ТЕСТОВЫЙ РЕЖИМ (заглушки вместо реальных платежей) ======
class PaymentError(Exception):
    pass

class YooMoneyPayment:
    def create_payment(self, amount, order_id, description):
        return {'payment_id': 'TESTPAY', 'payment_url': 'https://testpay.local', 'amount': amount, 'expires_at': None}
    def check_payment(self, payment_id):
        return 'completed'

class QiwiPayment:
    def create_payment(self, amount, order_id, description):
        return {'payment_id': 'TESTPAY', 'payment_url': 'https://testpay.local', 'amount': amount, 'expires_at': None}
    def check_payment(self, payment_id):
        return 'completed'

class CryptomusPayment:
    def create_payment(self, amount, order_id, description):
        return {'payment_id': 'TESTPAY', 'payment_url': 'https://testpay.local', 'amount': amount, 'expires_at': None}
    def check_payment(self, payment_id):
        return 'completed'

class PaymentManager:
    def __init__(self):
        self.yoomoney = YooMoneyPayment()
        self.qiwi = QiwiPayment()
        self.cryptomus = CryptomusPayment()
    def create_payment(self, method, amount, order_id, description):
        return {'payment_id': 'TESTPAY', 'payment_url': 'https://testpay.local', 'amount': amount, 'expires_at': None}
    def check_payment(self, method, payment_id):
        return 'completed'
    def get_available_methods(self):
        return ['yoomoney', 'qiwi', 'crypto']
payment_manager = PaymentManager()