from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("donations.donation_id"), nullable=False)
    payment_reference = Column(String(200), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    gateway = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
