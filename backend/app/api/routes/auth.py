from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import ACCESS_COOKIE_NAME
from app.db.session import get_db
from app.models import StaffUser
from app.schemas.auth import AuthenticatedUser, LoginRequest
from app.services.auth import (
    InvalidCredentialsError,
    authenticate_user,
    issue_access_token,
)

router = APIRouter(prefix="/auth", tags=["internal-auth"])
db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


@router.post("/login", response_model=AuthenticatedUser)
def login(
    payload: LoginRequest, response: Response, db: Session = db_dependency
) -> AuthenticatedUser:
    try:
        user = authenticate_user(db, payload.email, payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Cookie"},
        ) from exc

    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=issue_access_token(user),
        httponly=True,
        samesite="lax",
        secure=settings.env == "production",
        max_age=settings.jwt_access_token_expire_minutes * 60,
        path="/api",
    )
    return AuthenticatedUser.model_validate(user)


@router.get("/me", response_model=AuthenticatedUser)
def current_user(user: StaffUser = current_user_dependency) -> AuthenticatedUser:
    return AuthenticatedUser.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/api")
