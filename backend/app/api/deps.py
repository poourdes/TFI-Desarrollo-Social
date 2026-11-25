from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import ACCESS_COOKIE_NAME
from app.db.session import get_db
from app.models import StaffUser
from app.services.auth import user_from_token

access_cookie = Cookie(default=None, alias=ACCESS_COOKIE_NAME)
db_dependency = Depends(get_db)


def get_current_user(
    token: str | None = access_cookie,
    db: Session = db_dependency,
) -> StaffUser:
    user = user_from_token(db, token) if token else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida",
            headers={"WWW-Authenticate": "Cookie"},
        )
    return user
