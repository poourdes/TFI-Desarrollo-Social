from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import StaffRole, StaffUser
from app.schemas.panel import AdminUserCreateRequest, AdminUserResponse
from app.services.admin_users import AdminUserError, create_staff_user, list_staff_users
from app.services.areas import AreaLookupError

router = APIRouter(prefix="/panel/admin", tags=["internal-admin"])
db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


def _require_admin(user: StaffUser) -> None:
    if user.role is not StaffRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin puede gestionar usuarios",
        )


@router.get("/users", response_model=list[AdminUserResponse])
def list_users(
    db: Session = db_dependency, user: StaffUser = current_user_dependency
) -> list[AdminUserResponse]:
    _require_admin(user)
    users = list_staff_users(db)
    return [
        AdminUserResponse(
            id=item.id,
            email=item.email,
            full_name=item.full_name,
            role=item.role,
            active=item.active,
            areas=[
                {"id": str(a.id), "slug": a.slug, "nombre": a.nombre}
                for a in item.areas
            ],
        )
        for item in users
    ]


@router.post(
    "/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(
    payload: AdminUserCreateRequest,
    db: Session = db_dependency,
    user: StaffUser = current_user_dependency,
) -> AdminUserResponse:
    _require_admin(user)
    try:
        created = create_staff_user(
            db,
            actor_id=user.id,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            role=payload.role,
            area_slugs=payload.area_slugs,
            active=payload.active,
        )
    except AdminUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    except AreaLookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return AdminUserResponse(
        id=created.id,
        email=created.email,
        full_name=created.full_name,
        role=created.role,
        active=created.active,
        areas=[
            {"id": str(a.id), "slug": a.slug, "nombre": a.nombre} for a in created.areas
        ],
    )
