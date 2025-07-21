"""Utility functions for VPN Bot"""

import string
import random
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import qrcode
from io import BytesIO
import base64

logger = logging.getLogger(__name__)


def generate_referral_code(length: int = 8) -> str:
    """Generate unique referral code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_openvpn_config(user_id: int, server_url: str) -> str:
    """Generate OpenVPN configuration for user (simplified example)"""
    # В реальной реализации интегрировать с сервером OpenVPN
    return f"""
client
proto udp
remote {server_url} 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
auth SHA256
verb 3
<key>
USER_PRIVATE_KEY_{user_id}
</key>
<cert>
USER_CERT_{user_id}
</cert>
<ca>
CA_CERT_HERE
</ca>
<tls-auth>
TLS_AUTH_KEY_HERE
</tls-auth>
key-direction 1
    """

def generate_vpn_config(user_id: int, server_url: str, protocol: str = 'wireguard') -> str:
    """Generate VPN configuration for user (WireGuard or OpenVPN)"""
    if protocol == 'openvpn':
        return generate_openvpn_config(user_id, server_url)
    # По умолчанию WireGuard
    config_template = f"""[Interface]
PrivateKey = {generate_private_key()}
Address = 10.0.0.{user_id % 254 + 1}/32
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = SERVER_PUBLIC_KEY_HERE
Endpoint = {server_url}:51820
AllowedIPs = 0.0.0.0/0
"""
    return config_template


def generate_private_key() -> str:
    """Generate WireGuard private key (simplified)"""
    # In real implementation, use proper WireGuard key generation
    return base64.b64encode(hashlib.sha256(str(random.random()).encode()).digest()).decode()[:44]


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
    
    return datetime.utcnow() + timedelta(days=plan['duration_days'])


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    from bot.config.settings import Config
    return user_id in Config.ADMIN_IDS


def format_currency(amount: int) -> str:
    """Format amount in kopecks to rubles"""
    return f"{amount / 100:.0f} ₽"


def generate_payment_id() -> str:
    """Generate unique payment ID"""
    timestamp = int(datetime.utcnow().timestamp())
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


class PaymentManager:
    """Manage payments with different providers"""
    
    @staticmethod
    def create_yoomoney_payment(amount: int, description: str) -> Dict[str, str]:
        """Create YooMoney payment"""
        # Simplified implementation
        # In real app, integrate with YooMoney API
        payment_id = generate_payment_id()
        payment_url = f"https://yoomoney.ru/quickpay/confirm?receiver=RECEIVER&sum={amount/100}&label={payment_id}"
        
        return {
            'payment_id': payment_id,
            'payment_url': payment_url,
            'status': 'pending'
        }
    
    @staticmethod
    def create_qiwi_payment(amount: int, description: str) -> Dict[str, str]:
        """Create QIWI payment"""
        # Simplified implementation
        # In real app, integrate with QIWI API
        payment_id = generate_payment_id()
        payment_url = f"https://qiwi.com/payment/form?amount={amount/100}&currency=RUB&extra[account]={payment_id}"
        
        return {
            'payment_id': payment_id,
            'payment_url': payment_url,
            'status': 'pending'
        }
    
    @staticmethod
    def verify_payment(payment_id: str, payment_method: str) -> bool:
        """Verify payment status"""
        # In real implementation, check with payment provider API
        # For demo purposes, we'll simulate successful payment
        logger.info(f"Verifying payment {payment_id} via {payment_method}")
        return True


def setup_logging():
    """Setup logging configuration"""
    from bot.config.settings import Config
    
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/bot.log'),
            logging.StreamHandler()
        ]
    )
    
    # Reduce noise from telegram library
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)