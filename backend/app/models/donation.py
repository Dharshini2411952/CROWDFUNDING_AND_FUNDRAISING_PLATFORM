from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import synonym
from sqlalchemy.sql import func

from app.core.database import Base


class Donation(Base):

    __tablename__ = "donations"

    donation_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    donor_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.campaign_id"),
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    message = Column(
        Text,
        nullable=True
    )

    donation_date = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    payment_method = Column(
        String(50),
        default="UPI",
        nullable=True
    )

    transaction_id = Column(
        String(100),
        nullable=True
    )

    status = Column(
        String(50),
        default="SUCCESS",
        nullable=False
    )

    payment_status = synonym("status")
    created_at = synonym("donation_date")