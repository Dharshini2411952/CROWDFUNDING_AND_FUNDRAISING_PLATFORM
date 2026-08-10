from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ---------------- USER ----------------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    phone: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- CAMPAIGN ----------------

class CampaignCreate(BaseModel):
    creator_id: int
    title: str
    description: Optional[str] = None
    goal_amount: Decimal
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CampaignResponse(BaseModel):
    campaign_id: int
    creator_id: int
    title: str
    description: Optional[str] = None
    goal_amount: Decimal
    current_amount: Decimal
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- DONATION ----------------

class DonationCreate(BaseModel):
    campaign_id: int
    donor_id: int
    amount: Decimal
    message: Optional[str] = None
    payment_method: Optional[str] = None


class DonationResponse(BaseModel):
    donation_id: int
    campaign_id: int
    donor_id: int
    amount: Decimal
    message: Optional[str] = None
    donation_date: datetime
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


# ---------------- PAYMENT ----------------

class PaymentCreate(BaseModel):
    donation_id: int
    amount: Decimal
    method: str
    transaction_id: str


class PaymentResponse(BaseModel):
    payment_id: int
    donation_id: int
    amount: Decimal
    method: Optional[str] = None
    transaction_id: Optional[str] = None
    payment_date: datetime
    status: str

    class Config:
        from_attributes = True


# ---------------- REWARD ----------------

class RewardCreate(BaseModel):
    campaign_id: int
    title: str
    description: Optional[str] = None
    min_amount: Decimal
    quantity: int
    available_quantity: int


class RewardResponse(BaseModel):
    reward_id: int
    campaign_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    min_amount: Optional[Decimal] = None
    quantity: Optional[int] = None
    available_quantity: Optional[int] = None

    class Config:
        from_attributes = True


# ---------------- COMMENT ----------------

class CommentCreate(BaseModel):
    campaign_id: int
    user_id: int
    content: str


class CommentResponse(BaseModel):
    comment_id: int
    campaign_id: int
    user_id: int
    content: str
    commented_at: datetime

    class Config:
        from_attributes = True