import datetime as dt
import uuid
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(64))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    orders = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(32), default="pending")  # pending/paid/expired
    amount = Column(Integer, default=500)  # RUB in cents or TON 000
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    paid_at = Column(DateTime)
    wireguard_peer_public_key = Column(String(64))

    user = relationship("User", back_populates="orders")