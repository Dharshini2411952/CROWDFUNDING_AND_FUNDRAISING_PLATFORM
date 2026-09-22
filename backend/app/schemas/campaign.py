from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5)
    goal_amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=2, max_length=100)
    start_date: Optional[Union[datetime, str]] = None
    end_date: Optional[Union[datetime, str]] = None


class CampaignUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=200)
    description: Optional[str] = Field(default=None, min_length=5)
    goal_amount: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = Field(default=None, min_length=2, max_length=100)
    status: Optional[str] = None
    start_date: Optional[Union[datetime, str]] = None
    end_date: Optional[Union[datetime, str]] = None


class CampaignResponse(BaseModel):
    campaign_id: int
    title: str
    description: str
    goal_amount: float
    collected_amount: float
    category: str
    status: str
    creator_id: int
    start_date: Optional[Union[datetime, str]] = None
    end_date: Optional[Union[datetime, str]] = None
    created_at: Optional[Union[datetime, str]] = None

    class Config:
        from_attributes = True


class CampaignPaginatedResponse(BaseModel):
    items: list[CampaignResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
