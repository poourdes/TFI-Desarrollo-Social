from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import CaseStatus, StaffUser
from app.schemas.panel import (
    CaseDetail,
    CaseListItem,
    ContactResponse,
    EscalationConfirmRequest,
    TransitionRequest,
    VisitRequest,
)
from app.services.access import AreaAccessDenied
from app.services.cases import (
    CaseConflictError,
    CaseLookupError,
    ContactAccessDenied,
    ContactNotAvailableError,
    change_status,
    confirm_escalation,
    get_case_detail,
    list_cases,
    record_visit,
    reveal_contact,
)
from app.services.workflow import InvalidTransitionError

router = APIRouter(prefix="/panel", tags=["internal-panel"])
db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
status_query = Query(default=None, alias="status")


@router.get("/cases", response_model=list[CaseListItem])
def list_panel_cases(
    area_slug: str | None = None,
    status_filter: CaseStatus | None = status_query,
    db: Session = db_dependency,
    user: StaffUser = current_user_dependency,
) -> list[CaseListItem]:
    return list_cases(db, user, area_slug=area_slug, status=status_filter)


@router.get("/cases/{case_id}", response_model=CaseDetail)
def get_panel_case(
    case_id: UUID,
    db: Session = db_dependency,
    user: StaffUser = current_user_dependency,
) -> CaseDetail:
    try:
        return get_case_detail(db, user, case_id)
    except CaseLookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except AreaAccessDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc


@router.post("/cases/{case_id}/transition", response_model=CaseDetail)
def transition_panel_case(
    case_id: UUID,
    payload: TransitionRequest,
    db: Session = db_dependency,
    user: StaffUser = current_user_dependency,
) -> CaseDetail:
    try:
        return change_status(db, user, case_id, payload.target)
    except CaseLookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except AreaAccessDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except InvalidTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.post("/cases/{case_id}/visit", response_model=CaseDetail)
def visit_panel_case(
    case_id: UUID,
    payload: VisitRequest,
    db: Session = db_dependency,
    user: StaffUser = current_user_dependency,
) -> CaseDetail:
    try:
        return record_visit(
            db,
            user,
            case_id,
            scheduled_for=payload.scheduled_for,
            notes=payload.notes,
        )
    except CaseLookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except AreaAccessDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc


@router.post("/cases/{case_id}/escalation/confirm", response_model=CaseDetail)
def confirm_panel_escalation(
    case_id: UUID,
    payload: EscalationConfirmRequest,
    db: Session = db_dependency,
    user: StaffUser = current_user_dependency,
) -> CaseDetail:
    try:
        return confirm_escalation(db, user, case_id, note=payload.note)
    except CaseLookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except AreaAccessDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except CaseConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.get("/reports/{report_id}/contact", response_model=ContactResponse)
def get_report_contact(
    report_id: UUID,
    db: Session = db_dependency,
    user: StaffUser = current_user_dependency,
) -> ContactResponse:
    try:
        contact = reveal_contact(db, user, report_id)
    except (CaseLookupError, ContactNotAvailableError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except (AreaAccessDenied, ContactAccessDenied) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    return ContactResponse(report_id=report_id, contact=contact)
