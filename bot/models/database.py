"""Database models for VPN Telegram Bot"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    language_code = Column(String(10), default='ru')
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Referral system
    referrer_id = Column(Integer, ForeignKey('users.id'))
    referral_code = Column(String(20), unique=True)
    referral_balance = Column(Float, default=0.0)  # Баланс с рефералов
    total_referrals = Column(Integer, default=0)   # Общее количество рефералов
    
    # User stats
    total_spent = Column(Float, default=0.0)       # Общая потраченная сумма
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    referrals = relationship("User", remote_side=[id])
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"
    
    @property
    def full_name(self):
        """Get user's full name"""
        parts = [self.first_name, self.last_name]
        return ' '.join(filter(None, parts)) or self.username or f"User {self.telegram_id}"
    
    @property
    def active_subscription(self):
        """Get user's active subscription"""
        return next((sub for sub in self.subscriptions if sub.is_active and not sub.is_expired), None)
    
    @property
    def has_active_subscription(self):
        """Check if user has active subscription"""
        return self.active_subscription is not None


class Subscription(Base):
    """Subscription model"""
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_type = Column(String(50), nullable=False)  # 1_month, 3_months, etc.
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    vpn_config = Column(Text)  # VPN configuration data
    config_name = Column(String(255))  # Имя конфигурации
    server_location = Column(String(100))  # Локация сервера
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(user_id={self.user_id}, plan={self.plan_type}, active={self.is_active})>"
    
    @property
    def is_expired(self):
        """Check if subscription is expired"""
        return datetime.utcnow() > self.end_date
    
    @property
    def days_remaining(self):
        """Get days remaining in subscription"""
        if self.is_expired:
            return 0
        return (self.end_date - datetime.utcnow()).days
    
    @property
    def time_remaining_text(self):
        """Get human-readable time remaining"""
        if self.is_expired:
            return "Истекла"
        
        diff = self.end_date - datetime.utcnow()
        days = diff.days
        
        if days > 30:
            months = days // 30
            return f"{months} мес."
        elif days > 0:
            return f"{days} дн."
        else:
            hours = diff.seconds // 3600
            return f"{hours} ч."


class Payment(Base):
    """Payment model"""
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Integer, nullable=False)  # Amount in kopecks
    currency = Column(String(3), default='RUB')
    plan_type = Column(String(50), nullable=False)
    payment_method = Column(String(50))  # yoomoney, qiwi, crypto
    payment_id = Column(String(255))  # External payment ID
    payment_url = Column(String(500))  # Payment URL for user
    status = Column(String(20), default='pending')  # pending, completed, failed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)  # Время истечения счета
    
    # Relationships
    user = relationship("User", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(user_id={self.user_id}, amount={self.amount}, status={self.status})>"
    
    @property
    def amount_rubles(self):
        """Get amount in rubles"""
        return self.amount / 100
    
    @property
    def is_expired(self):
        """Check if payment is expired"""
        return self.expires_at and datetime.utcnow() > self.expires_at


class VPNKey(Base):
    """VPN Key model for managing available keys"""
    __tablename__ = 'vpn_keys'
    
    id = Column(Integer, primary_key=True)
    key_data = Column(Text, nullable=False)  # VPN configuration or key
    server_location = Column(String(100))  # Server location
    is_used = Column(Boolean, default=False)
    assigned_user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime)
    
    def __repr__(self):
        return f"<VPNKey(id={self.id}, is_used={self.is_used}, location={self.server_location})>"


class ReferralPayout(Base):
    """Referral payout model"""
    __tablename__ = 'referral_payouts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)  # Amount in rubles
    status = Column(String(20), default='pending')  # pending, completed, failed
    payment_method = Column(String(50))
    payment_details = Column(String(500))  # Card number, wallet, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<ReferralPayout(user_id={self.user_id}, amount={self.amount}, status={self.status})>"


class AdminLog(Base):
    """Admin action logs"""
    __tablename__ = 'admin_logs'
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(255), nullable=False)
    target_user_id = Column(Integer, ForeignKey('users.id'))
    details = Column(Text)
    ip_address = Column(String(45))  # IPv4 or IPv6
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AdminLog(admin_id={self.admin_id}, action={self.action})>"


class BotStats(Base):
    """Bot statistics model"""
    __tablename__ = 'bot_stats'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    total_users = Column(Integer, default=0)
    active_subscriptions = Column(Integer, default=0)
    daily_revenue = Column(Float, default=0.0)
    new_users = Column(Integer, default=0)
    new_payments = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<BotStats(date={self.date.date()}, users={self.total_users})>"


class DatabaseManager:
    """Database management class"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
        
    def close(self):
        """Close database connection"""
        self.engine.dispose()