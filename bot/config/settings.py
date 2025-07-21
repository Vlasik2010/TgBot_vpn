"""
Configuration module for VPN Telegram Bot
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Bot configuration settings"""
    
    # Telegram Bot Settings
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
    
    # Database Settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///vpn_bot.db')
    
    # Payment Settings
    YOOMONEY_TOKEN = os.getenv('YOOMONEY_TOKEN')
    QIWI_TOKEN = os.getenv('QIWI_TOKEN')
    CRYPTOMUS_API_KEY = os.getenv('CRYPTOMUS_API_KEY')
    CRYPTOMUS_MERCHANT_ID = os.getenv('CRYPTOMUS_MERCHANT_ID')
    
    # VPN Settings
    VPN_SERVER_URL = os.getenv('VPN_SERVER_URL')
    VPN_API_KEY = os.getenv('VPN_API_KEY')
    
    # Bot Settings
    DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'ru')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Subscription Plans (in rubles)
    PLAN_1_MONTH_PRICE = int(os.getenv('PLAN_1_MONTH_PRICE', 299))
    PLAN_3_MONTH_PRICE = int(os.getenv('PLAN_3_MONTH_PRICE', 799))
    PLAN_6_MONTH_PRICE = int(os.getenv('PLAN_6_MONTH_PRICE', 1499))
    PLAN_12_MONTH_PRICE = int(os.getenv('PLAN_12_MONTH_PRICE', 2699))
    
    # Referral System
    REFERRAL_BONUS_PERCENT = int(os.getenv('REFERRAL_BONUS_PERCENT', 10))
    REFERRAL_MIN_PAYOUT = int(os.getenv('REFERRAL_MIN_PAYOUT', 100))
    
    # Support Configuration
    SUPPORT_USERNAME = os.getenv('SUPPORT_USERNAME')
    SUPPORT_CHAT_ID = os.getenv('SUPPORT_CHAT_ID')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        if not cls.ADMIN_IDS:
            raise ValueError("At least one ADMIN_ID is required")
        return True


# Subscription plans configuration
SUBSCRIPTION_PLANS = {
    '1_month': {
        'name': '1 месяц',
        'price': Config.PLAN_1_MONTH_PRICE,
        'duration_days': 30,
        'description': '🚀 Базовый план на 1 месяц',
        'emoji': '🥉',
        'popular': False
    },
    '3_months': {
        'name': '3 месяца',
        'price': Config.PLAN_3_MONTH_PRICE,
        'duration_days': 90,
        'description': '🔥 Популярный план на 3 месяца',
        'emoji': '🥈',
        'popular': True
    },
    '6_months': {
        'name': '6 месяцев',
        'price': Config.PLAN_6_MONTH_PRICE,
        'duration_days': 180,
        'description': '💎 Выгодный план на полгода',
        'emoji': '🥇',
        'popular': False
    },
    '12_months': {
        'name': '1 год',
        'price': Config.PLAN_12_MONTH_PRICE,
        'duration_days': 365,
        'description': '👑 Максимальная выгода на целый год',
        'emoji': '💰',
        'popular': False
    }
}

# Payment methods configuration
PAYMENT_METHODS = {
    'yoomoney': {
        'name': 'ЮMoney',
        'emoji': '💳',
        'description': 'Банковские карты, электронные кошельки'
    },
    'qiwi': {
        'name': 'QIWI',
        'emoji': '🥝',
        'description': 'QIWI кошелек, банковские карты'
    },
    'crypto': {
        'name': 'Криптовалюты',
        'emoji': '₿',
        'description': 'Bitcoin, Ethereum, USDT и другие'
    }
}