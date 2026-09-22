from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import synonym
from sqlalchemy.sql import func

from app.core.database import Base


class Campaign(Base):

    __tablename__ = "campaigns"

    campaign_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    goal_amount = Column(Float, nullable=False)
    collected_amount = Column(Float, default=0.0, nullable=False)
    category = Column(String(100), nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)
    creator_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    current_amount = synonym("collected_amount")