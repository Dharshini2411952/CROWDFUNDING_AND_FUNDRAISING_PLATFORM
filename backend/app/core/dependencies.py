from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user as _get_current_user
from app.models.user import User


def get_current_user(
    credentials: object = Depends(_get_current_user),
    db: Session = Depends(get_db),
) -> User:
    return credentials
