"""
FinPilot AI — Database Models (PostgreSQL via SQLAlchemy)
"""

import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, String, Float, Integer,
    Boolean, DateTime, JSON, Text, ForeignKey, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import uuid

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./finpilot_dev.db"  # SQLite fallback for dev/HF Spaces
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)


# ─────────────────────────────────────────────
#  Models
# ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String(20), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    name = Column(String(100))
    country_code = Column(String(10), default="+91")
    plan = Column(String(20), default="free")   # free | pro | premium
    currency = Column(String(10), default="INR")
    language = Column(String(20), default="English")
    theme = Column(String(20), default="pastel")
    accent_color = Column(String(30), default="rose")
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=True)
    whatsapp_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String(100), nullable=True)
    paypal_email = Column(String(255), nullable=True)

    # Relationships
    financial_states = relationship("FinancialState", back_populates="user",
                                     cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user",
                                  cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user",
                                  cascade="all, delete-orphan")


class FinancialState(Base):
    __tablename__ = "financial_states"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    month = Column(Integer, default=0)
    income = Column(Float, default=0)
    expenses = Column(JSON, default={})
    savings = Column(Float, default=0)
    debt = Column(Float, default=0)
    investments = Column(Float, default=0)
    emergency_fund = Column(Float, default=0)
    net_worth = Column(Float, default=0)
    health_score = Column(Integer, default=0)
    savings_rate = Column(Float, default=0)
    life_event = Column(String(50), default="none")
    currency = Column(String(10), default="INR")
    task = Column(String(50), default="wealth_building")
    ai_action = Column(JSON, nullable=True)
    ai_reasoning = Column(Text, nullable=True)
    reward = Column(Float, nullable=True)
    snapshot = Column(JSON, default={})  # Full state snapshot
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="financial_states")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    name = Column(String(200))
    category = Column(String(50))   # emergency | retirement | purchase | travel | education
    target_amount = Column(Float)
    current_amount = Column(Float, default=0)
    monthly_contribution = Column(Float, default=0)
    target_date = Column(DateTime, nullable=True)
    annual_return = Column(Float, default=12.0)
    currency = Column(String(10), default="INR")
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="goals")

    @property
    def progress_pct(self):
        if self.target_amount <= 0:
            return 0
        return min(100, round(self.current_amount / self.target_amount * 100, 1))


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    title = Column(String(200))
    body = Column(Text)
    type = Column(String(50))       # alert | reminder | ai_insight | achievement | warning
    channel = Column(String(50))    # in_app | email | sms | whatsapp | push
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    priority = Column(Integer, default=2)   # 1=high 2=normal 3=low
    metadata = Column(JSON, default={})
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    plan = Column(String(20))           # free | pro | premium
    status = Column(String(20))        # active | cancelled | expired | trial
    billing_cycle = Column(String(20)) # monthly | annual
    amount = Column(Float)
    currency = Column(String(10), default="INR")
    payment_method = Column(String(50)) # paypal | stripe | razorpay
    payment_id = Column(String(200), nullable=True)
    starts_at = Column(DateTime, default=datetime.utcnow)
    ends_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="subscriptions")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    month = Column(Integer)
    year = Column(Integer)
    content = Column(Text)              # Full AI-generated report
    summary = Column(JSON, default={})  # Key metrics snapshot
    pdf_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    base = Column(String(10))
    target = Column(String(10))
    rate = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow)