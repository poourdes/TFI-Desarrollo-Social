from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_access_token, verify_password
from app.models import StaffUser


class InvalidCredentialsError(ValueError):
    pass


def authenticate_user(db: Session, email: str, password: str) -> StaffUser:
    normalized = email.strip().lower()
    user = db.scalar(select(StaffUser).where(StaffUser.email == normalized))
    if (
        user is None
        or not user.active
        or user.password_hash is None
        or not verify_password(password, user.password_hash)
    ):
        raise InvalidCredentialsError("Credenciales inválidas")
    return user


def issue_access_token(user: StaffUser) -> str:
    return create_access_token(user.id)


def user_from_token(db: Session, token: str) -> StaffUser | None:
    user_id: UUID | None = decode_access_token(token)
    if user_id is None:
        return None
    user = db.get(StaffUser, user_id)
    if user is None or not user.active:
        return None
    return user
