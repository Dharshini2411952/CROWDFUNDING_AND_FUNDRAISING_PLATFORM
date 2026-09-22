from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel


class NotificationRead(BaseModel):
    notification_id: int
    user_id: int
    title: str
    message: str
    notification_type: Optional[str] = None
    is_read: bool
    created_at: Optional[Union[datetime, str]] = None

    class Config:
        from_attributes = True
