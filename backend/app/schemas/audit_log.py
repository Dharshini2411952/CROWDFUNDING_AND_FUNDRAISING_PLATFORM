from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel


class AuditLogRead(BaseModel):
    audit_id: int
    admin_id: int
    admin_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[str] = None
    created_at: Optional[Union[datetime, str]] = None

    class Config:
        from_attributes = True
