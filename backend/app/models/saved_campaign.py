from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func

from app.core.database import Base


class SavedCampaign(Base):
    __tablename__ = "saved_campaigns"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True, nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"), primary_key=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
