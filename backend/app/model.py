from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    campaigns = relationship("Campaign", back_populates="creator")
    donations = relationship("Donation", back_populates="donor")
    comments = relationship("Comment", back_populates="user")


class Campaign(Base):
    __tablename__ = "campaigns"

    campaign_id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.user_id"))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    goal_amount = Column(DECIMAL(10, 2), nullable=False)
    current_amount = Column(DECIMAL(10, 2), default=0)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(30), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="campaigns")
    donations = relationship("Donation", back_populates="campaign")
    rewards = relationship("Reward", back_populates="campaign")
    comments = relationship("Comment", back_populates="campaign")


class Donation(Base):
    __tablename__ = "donations"

    donation_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"))
    donor_id = Column(Integer, ForeignKey("users.user_id"))
    amount = Column(DECIMAL(10, 2), nullable=False)
    message = Column(Text)
    donation_date = Column(DateTime, default=datetime.utcnow)
    payment_method = Column(String(50))
    transaction_id = Column(String(100))
    status = Column(String(30), default="PENDING")

    campaign = relationship("Campaign", back_populates="donations")
    donor = relationship("User", back_populates="donations")
    payment = relationship("Payment", back_populates="donation", uselist=False)


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("donations.donation_id"))
    amount = Column(DECIMAL(10, 2), nullable=False)
    method = Column(String(50))
    transaction_id = Column(String(100))
    payment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(30), default="SUCCESS")

    donation = relationship("Donation", back_populates="payment")


class Reward(Base):
    __tablename__ = "rewards"

    reward_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"))
    title = Column(String(150))
    description = Column(Text)
    min_amount = Column(DECIMAL(10, 2))
    quantity = Column(Integer)
    available_quantity = Column(Integer)

    campaign = relationship("Campaign", back_populates="rewards")


class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    content = Column(Text, nullable=False)
    commented_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="comments")
    user = relationship("User", back_populates="comments")