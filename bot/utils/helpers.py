"""Utility functions for VPN Bot"""

import string
import random
import hashlib
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import qrcode
from io import BytesIO
import base64

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging configuration"""
    from bot.config.settings import Config
    
    # Create logs directory if not exists
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler(
        f'logs/vpn_bot_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.setLevel(log_level)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Suppress noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


def generate_referral_code(length: int = 8) -> str:
    """Generate unique referral code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_vpn_config(user_id: int, server_location: str = "Netherlands") -> str:
    """Generate VPN configuration for user"""
    # Generate unique keys for user
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    
    # Assign unique IP address
    ip_suffix = (user_id % 254) + 1
    client_ip = f"10.0.0.{ip_suffix}/32"
    
    config_template = f"""[Interface]
PrivateKey = {private_key}
Address = {client_ip}
DNS = 1.1.1.1, 8.8.8.8
MTU = 1420

[Peer]
PublicKey = SERVER_PUBLIC_KEY_PLACEHOLDER
Endpoint = {get_server_endpoint(server_location)}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
    return config_template


def generate_private_key() -> str:
    """Generate WireGuard private key (simplified for demo)"""
    # In production, use proper WireGuard key generation
    key_bytes = os.urandom(32)
    return base64.b64encode(key_bytes).decode('utf-8')


def generate_public_key(private_key: str) -> str:
    """Generate public key from private key (simplified for demo)"""
    # In production, use proper WireGuard key derivation
    hash_obj = hashlib.sha256(private_key.encode())
    key_bytes = hash_obj.digest()
    return base64.b64encode(key_bytes).decode('utf-8')


def get_server_endpoint(location: str) -> str:
    """Get server endpoint for location"""
    servers = {
        "Netherlands": "nl.vpnserver.com:51820",
        "Germany": "de.vpnserver.com:51820",
        "France": "fr.vpnserver.com:51820",
        "United States": "us.vpnserver.com:51820",
        "Japan": "jp.vpnserver.com:51820",
        "Singapore": "sg.vpnserver.com:51820"
    }
    return servers.get(location, "nl.vpnserver.com:51820")


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


def format_time_ago(dt: datetime) -> str:
    """Format time ago in Russian"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} дн. назад"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} ч. назад"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} мин. назад"
    else:
        return "только что"


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


def validate_email(email: str) -> bool:
    """Validate email address"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def get_user_display_name(user) -> str:
    """Get user display name from telegram user object"""
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    elif user.username:
        return f"@{user.username}"
    else:
        return f"User {user.id}"


def calculate_referral_bonus(amount: int) -> int:
    """Calculate referral bonus amount"""
    from bot.config.settings import Config
    return int(amount * Config.REFERRAL_BONUS_PERCENT / 100)


def generate_config_filename(user_id: int, plan_type: str) -> str:
    """Generate VPN config filename"""
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"vpn_config_{user_id}_{plan_type}_{timestamp}.conf"


def get_plan_emoji(plan_type: str) -> str:
    """Get emoji for plan type"""
    emojis = {
        '1_month': '🥉',
        '3_months': '🥈',
        '6_months': '🥇',
        '12_months': '💰'
    }
    return emojis.get(plan_type, '📦')


def get_server_flag(location: str) -> str:
    """Get flag emoji for server location"""
    flags = {
        "Netherlands": "🇳🇱",
        "Germany": "🇩🇪",
        "France": "🇫🇷",
        "United States": "🇺🇸",
        "Japan": "🇯🇵",
        "Singapore": "🇸🇬",
        "United Kingdom": "🇬🇧",
        "Canada": "🇨🇦",
        "Australia": "🇦🇺"
    }
    return flags.get(location, "🌍")


def create_referral_link(referral_code: str, bot_username: str) -> str:
    """Create referral link"""
    return f"https://t.me/{bot_username}?start={referral_code}"


def log_admin_action(admin_id: int, action: str, target_user_id: Optional[int] = None, details: Optional[str] = None):
    """Log admin action to database"""
    from bot.models.database import DatabaseManager, AdminLog
    from bot.config.settings import Config
    
    db_manager = DatabaseManager(Config.DATABASE_URL)
    session = db_manager.get_session()
    
    try:
        log_entry = AdminLog(
            admin_id=admin_id,
            action=action,
            target_user_id=target_user_id,
            details=details
        )
        session.add(log_entry)
        session.commit()
        logger.info(f"Admin action logged: {admin_id} - {action}")
    except Exception as e:
        logger.error(f"Failed to log admin action: {e}")
        session.rollback()
    finally:
        session.close()


def update_user_activity(user_id: int):
    """Update user's last activity timestamp"""
    from bot.models.database import DatabaseManager, User
    from bot.config.settings import Config
    
    db_manager = DatabaseManager(Config.DATABASE_URL)
    session = db_manager.get_session()
    
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if user:
            user.last_activity = datetime.utcnow()
            session.commit()
    except Exception as e:
        logger.error(f"Failed to update user activity: {e}")
        session.rollback()
    finally:
        session.close()


def get_random_server_location() -> str:
    """Get random server location for load balancing"""
    locations = ["Netherlands", "Germany", "France", "United States", "Japan", "Singapore"]
    return random.choice(locations)


def create_config_file(config_data: str, filename: str) -> BytesIO:
    """Create configuration file as BytesIO"""
    file_buffer = BytesIO()
    file_buffer.write(config_data.encode('utf-8'))
    file_buffer.seek(0)
    file_buffer.name = filename
    return file_buffer


class StatsCalculator:
    """Statistics calculation utilities"""
    
    @staticmethod
    def calculate_daily_stats():
        """Calculate daily statistics"""
        from bot.models.database import DatabaseManager, User, Payment, Subscription
        from bot.config.settings import Config
        
        db_manager = DatabaseManager(Config.DATABASE_URL)
        session = db_manager.get_session()
        
        try:
            today = datetime.utcnow().date()
            
            # New users today
            new_users = session.query(User).filter(
                User.created_at >= today
            ).count()
            
            # Successful payments today
            successful_payments = session.query(Payment).filter(
                Payment.created_at >= today,
                Payment.status == 'completed'
            ).count()
            
            # Daily revenue
            revenue_result = session.query(Payment).filter(
                Payment.created_at >= today,
                Payment.status == 'completed'
            ).all()
            
            daily_revenue = sum(p.amount_rubles for p in revenue_result)
            
            # Active subscriptions
            active_subscriptions = session.query(Subscription).filter(
                Subscription.is_active == True,
                Subscription.end_date > datetime.utcnow()
            ).count()
            
            return {
                'new_users': new_users,
                'successful_payments': successful_payments,
                'daily_revenue': daily_revenue,
                'active_subscriptions': active_subscriptions
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate daily stats: {e}")
            return {
                'new_users': 0,
                'successful_payments': 0,
                'daily_revenue': 0.0,
                'active_subscriptions': 0
            }
        finally:
            session.close()


# Import payment manager
from bot.utils.payments import payment_manager, PaymentError