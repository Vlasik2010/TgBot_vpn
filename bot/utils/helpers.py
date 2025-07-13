"""Utility functions for VPN Bot"""

import string
import random
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import qrcode
from io import BytesIO
import base64

logger = logging.getLogger(__name__)


def generate_referral_code(length: int = 8) -> str:
    """Generate unique referral code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_vpn_config(user_id: int, server_url: str) -> str:
    """Generate VPN configuration for user"""
    # Generate unique private key for user
    private_key = generate_private_key()
    
    # Generate unique IP address for user
    ip_suffix = (user_id % 253) + 2  # Range 2-254
    user_ip = f"10.0.0.{ip_suffix}/32"
    
    # WireGuard configuration template
    config_template = f"""[Interface]
PrivateKey = {private_key}
Address = {user_ip}
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = SERVER_PUBLIC_KEY_PLACEHOLDER
Endpoint = {server_url}:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
    return config_template


def generate_private_key() -> str:
    """Generate WireGuard private key (simplified but more realistic)"""
    # Generate 32 random bytes and encode to base64
    import secrets
    key_bytes = secrets.token_bytes(32)
    return base64.b64encode(key_bytes).decode('ascii')


def create_qr_code(data: str) -> BytesIO:
    """Create QR code from data"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return img_buffer


def format_datetime(dt: datetime) -> str:
    """Format datetime for Russian locale"""
    return dt.strftime("%d.%m.%Y %H:%M")


def format_date(dt: datetime) -> str:
    """Format date for Russian locale"""
    return dt.strftime("%d.%m.%Y")


def calculate_end_date(plan_type: str) -> datetime:
    """Calculate subscription end date based on plan"""
    from bot.config.settings import SUBSCRIPTION_PLANS
    
    plan = SUBSCRIPTION_PLANS.get(plan_type)
    if not plan:
        raise ValueError(f"Unknown plan type: {plan_type}")
    
    return datetime.now(timezone.utc) + timedelta(days=plan['duration_days'])


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    from bot.config.settings import Config
    return user_id in Config.ADMIN_IDS


def format_currency(amount: int) -> str:
    """Format amount in kopecks to rubles"""
    return f"{amount / 100:.0f} ₽"


def generate_payment_id() -> str:
    """Generate unique payment ID"""
    timestamp = int(datetime.now(timezone.utc).timestamp())
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"VPN_{timestamp}_{random_part}"


def validate_telegram_data(data: Dict[str, Any]) -> bool:
    """Validate telegram webhook data"""
    # Add telegram data validation logic here
    required_fields = ['message', 'from']
    return all(field in data for field in required_fields)


def sanitize_input(text: str, max_length: int = 255) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potential harmful characters
    sanitized = ''.join(char for char in text if char.isprintable())
    return sanitized[:max_length].strip()


def log_admin_action(admin_id: int, action: str, target_user_id: Optional[int] = None, details: Optional[str] = None):
    """Log admin actions"""
    from bot.models.database import DatabaseManager, AdminLog
    from bot.config.settings import Config
    
    try:
        db = DatabaseManager(Config.DATABASE_URL)
        session = db.get_session()
        
        log_entry = AdminLog(
            admin_id=admin_id,
            action=action,
            target_user_id=target_user_id,
            details=details
        )
        
        session.add(log_entry)
        session.commit()
        session.close()
        
        logger.info(f"Admin action logged: {admin_id} - {action}")
    except Exception as e:
        logger.error(f"Failed to log admin action: {e}")


class VPNManager:
    """Manage VPN server integration"""
    
    @staticmethod
    def create_vpn_user(user_id: int, username: str) -> Dict[str, str]:
        """Create VPN user on server (placeholder implementation)"""
        from bot.config.settings import Config
        
        # In real implementation, this would call VPN server API
        private_key = generate_private_key()
        public_key = f"PUBLIC_KEY_FOR_USER_{user_id}"
        
        return {
            'private_key': private_key,
            'public_key': public_key,
            'ip_address': f"10.0.0.{(user_id % 253) + 2}",
            'config': generate_vpn_config(user_id, Config.VPN_SERVER_URL or "vpn.example.com")
        }
    
    @staticmethod
    def delete_vpn_user(user_id: int) -> bool:
        """Delete VPN user from server"""
        # In real implementation, this would call VPN server API
        logger.info(f"Removing VPN access for user {user_id}")
        return True
    
    @staticmethod
    def check_vpn_server_status() -> bool:
        """Check VPN server health"""
        # In real implementation, ping VPN server
        return True


class PaymentManager:
    """Manage payments with different providers"""
    
    @staticmethod
    def create_yoomoney_payment(amount: int, description: str) -> Dict[str, str]:
        """Create YooMoney payment"""
        from bot.config.settings import Config
        
        payment_id = generate_payment_id()
        
        # Real YooMoney integration would use their API
        if Config.YOOMONEY_TOKEN and Config.YOOMONEY_TOKEN != 'test_yoomoney_token':
            # TODO: Integrate with real YooMoney API
            payment_url = f"https://yoomoney.ru/quickpay/confirm?receiver=RECEIVER&sum={amount/100}&label={payment_id}"
        else:
            # Test/demo payment URL
            payment_url = f"https://demo.payment.com/pay?amount={amount/100}&id={payment_id}"
        
        return {
            'payment_id': payment_id,
            'payment_url': payment_url,
            'status': 'pending'
        }
    
    @staticmethod
    def create_qiwi_payment(amount: int, description: str) -> Dict[str, str]:
        """Create QIWI payment"""
        from bot.config.settings import Config
        
        payment_id = generate_payment_id()
        
        # Real QIWI integration would use their API
        if Config.QIWI_TOKEN and Config.QIWI_TOKEN != 'test_qiwi_token':
            # TODO: Integrate with real QIWI API
            payment_url = f"https://qiwi.com/payment/form?amount={amount/100}&currency=RUB&extra[account]={payment_id}"
        else:
            # Test/demo payment URL
            payment_url = f"https://demo.qiwi.com/pay?amount={amount/100}&id={payment_id}"
        
        return {
            'payment_id': payment_id,
            'payment_url': payment_url,
            'status': 'pending'
        }
    
    @staticmethod
    def create_crypto_payment(amount: int, description: str) -> Dict[str, str]:
        """Create cryptocurrency payment"""
        payment_id = generate_payment_id()
        
        # Calculate approximate BTC amount (simplified)
        btc_amount = amount / 100 / 50000  # Assuming 1 BTC = 50000 RUB
        
        # Bitcoin payment URL
        payment_url = f"bitcoin:bc1qexampleaddress?amount={btc_amount:.8f}&label=VPN_{payment_id}"
        
        return {
            'payment_id': payment_id,
            'payment_url': payment_url,
            'status': 'pending',
            'btc_amount': f"{btc_amount:.8f}"
        }
    
    @staticmethod
    def verify_payment(payment_id: str, payment_method: str) -> bool:
        """Verify payment status"""
        # In real implementation, check with payment provider API
        # For demo purposes, we'll simulate successful payment
        logger.info(f"Verifying payment {payment_id} via {payment_method}")
        
        # In test mode, always return True for demo
        from bot.config.settings import Config
        if Config.DEBUG:
            return True
        
        # Real verification logic would go here
        return True


def setup_logging():
    """Setup logging configuration"""
    from bot.config.settings import Config
    import os
    
    # Create logs directory if it doesn't exist
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, 'bot.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Configure specific loggers
    loggers_config = {
        'telegram': logging.WARNING,
        'httpx': logging.WARNING,
        'urllib3': logging.WARNING,
        'sqlalchemy.engine': logging.WARNING if not Config.DEBUG else logging.INFO,
    }
    
    for logger_name, level in loggers_config.items():
        logging.getLogger(logger_name).setLevel(level)
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.info(f"Log level: {Config.LOG_LEVEL}")
    logger.info(f"Debug mode: {Config.DEBUG}")