from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.area import PublicAreasResponse
from app.services.areas import build_public_areas

router = APIRouter(prefix="/areas", tags=["public-areas"])
db_dependency = Depends(get_db)


@router.get("", response_model=PublicAreasResponse)
def list_areas_endpoint(db: Session = db_dependency) -> PublicAreasResponse:
    return build_public_areas(db)
