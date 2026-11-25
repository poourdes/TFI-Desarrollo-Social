from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.report import (
    ReportCreate,
    ReportCreatedResponse,
    TrackingEvent,
    TrackingRequest,
    TrackingStatusResponse,
)
from app.services.areas import (
    AreaLookupError,
    FormValidationError,
    get_active_area,
    parse_area_config,
)
from app.services.captcha import CaptchaVerificationError, get_captcha_provider
from app.services.rate_limit import enforce_rate_limit
from app.services.reports import create_report, get_tracked_report

router = APIRouter(prefix="/reports", tags=["public-reports"])
db_dependency = Depends(get_db)


@router.post("/track", response_model=TrackingStatusResponse)
def track_report_endpoint(
    payload: TrackingRequest, request: Request, db: Session = db_dependency
) -> TrackingStatusResponse:
    enforce_rate_limit(request, "reports-track", limit=15, window_seconds=60)
    tracked = get_tracked_report(db, payload.tracking_code)
    if tracked is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="No se encontró una denuncia con ese código.",
        )
    return TrackingStatusResponse(
        case_number=tracked.case_number,
        case_status=tracked.case_status,
        created_at=tracked.created_at,
        timeline=[
            TrackingEvent(
                event_type=event.event_type,
                message=event.public_message,
                created_at=event.created_at,
            )
            for event in tracked.timeline
        ],
    )


@router.post(
    "/{area_slug}",
    response_model=ReportCreatedResponse,
    status_code=http_status.HTTP_201_CREATED,
)
def create_report_endpoint(
    area_slug: str,
    payload: ReportCreate,
    request: Request,
    db: Session = db_dependency,
) -> ReportCreatedResponse:
    enforce_rate_limit(request, "reports-create", limit=10, window_seconds=60)
    try:
        get_captcha_provider().verify(payload.captcha_token)
    except CaptchaVerificationError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    try:
        area = get_active_area(db, area_slug)
    except AreaLookupError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

    config = parse_area_config(area)
    try:
        created = create_report(db, area, config, payload)
    except FormValidationError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc

    return ReportCreatedResponse(
        tracking_code=created.tracking_code,
        case_number=created.case_number,
        area_slug=area.slug,
        status=created.report.status,
        created_at=created.report.created_at,
    )
