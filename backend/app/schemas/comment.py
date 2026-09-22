from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    campaign_id: int
    comment_text: str = Field(..., min_length=1, max_length=2000)


class CommentUpdate(BaseModel):
    comment_text: str = Field(..., min_length=1, max_length=2000)


class CommentRead(BaseModel):
    comment_id: int
    user_id: int
    campaign_id: int
    comment_text: str
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None
    user_name: str

    class Config:
        from_attributes = True
