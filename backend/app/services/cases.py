from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import (
    AuditAction,
    Case,
    CaseEvent,
    CaseEventType,
    CaseStatus,
    Report,
    StaffUser,
)
from app.schemas.area_config import AreaConfig
from app.schemas.panel import CaseDetail, CaseListItem, PanelEvent, PanelReport
from app.services.access import AreaAccessDenied, assert_area_access, visible_cases
from app.services.areas import parse_area_config
from app.services.audit import record_audit
from app.services.contact import decrypt_contact
from app.services.workflow import assert_transition_allowed


class CaseLookupError(LookupError):
    pass


class CaseConflictError(ValueError):
    pass


class ContactAccessDenied(PermissionError):
    pass


class ContactNotAvailableError(LookupError):
    pass


def _case_access_denied(
    db: Session, user: StaffUser, case: Case, reason: str | None = None
) -> AreaAccessDenied:
    details: dict[str, object] = {"area_slug": case.area.slug}
    if reason is not None:
        details["reason"] = reason
    record_audit(
        db,
        action=AuditAction.area_access_denied,
        entity_type="case",
        entity_id=case.id,
        actor_id=user.id,
        details=details,
    )
    db.commit()
    return AreaAccessDenied(f"Acceso denegado al área {case.area.slug}")


def _load_case(db: Session, case_id: UUID) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise CaseLookupError("Caso no encontrado")
    return case


def _assert_case_access(db: Session, user: StaffUser, case: Case) -> None:
    try:
        assert_area_access(user, case.area)
    except AreaAccessDenied:
        raise _case_access_denied(db, user, case) from None


def _pending_escalation(case: Case) -> bool:
    return any(
        event.event_type is CaseEventType.escalation_suggested for event in case.events
    ) and not any(
        event.event_type is CaseEventType.escalation_confirmed for event in case.events
    )


def _sort_key(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _case_detail(case: Case, config: AreaConfig) -> CaseDetail:
    events = sorted(case.events, key=lambda event: _sort_key(event.created_at))
    reports = sorted(case.reports, key=lambda report: _sort_key(report.created_at))
    return CaseDetail(
        id=case.id,
        case_number=case.case_number,
        area_slug=case.area.slug,
        area_name=case.area.nombre,
        status=case.status,
        created_at=case.created_at,
        allowed_transitions=config.workflow.transitions.get(case.status, []),
        pending_escalation=_pending_escalation(case),
        reports=[
            PanelReport(
                id=report.id,
                situation_type=report.situation_type,
                locality=report.locality,
                address=report.address,
                description=report.description,
                status=report.status,
                incident_date=report.incident_date,
                created_at=report.created_at,
                has_contact=report.contact is not None,
            )
            for report in reports
        ],
        timeline=[
            PanelEvent(
                event_type=event.event_type,
                message=event.public_message,
                created_at=event.created_at,
            )
            for event in events
        ],
    )


def list_cases(
    db: Session,
    user: StaffUser,
    *,
    area_slug: str | None = None,
    status: CaseStatus | None = None,
) -> list[CaseListItem]:
    cases = visible_cases(db, user)
    if area_slug is not None:
        cases = [case for case in cases if case.area.slug == area_slug]
    if status is not None:
        cases = [case for case in cases if case.status is status]
    return [
        CaseListItem(
            id=case.id,
            case_number=case.case_number,
            area_slug=case.area.slug,
            area_name=case.area.nombre,
            status=case.status,
            report_count=len(case.reports),
            created_at=case.created_at,
        )
        for case in cases
    ]


def get_case_detail(db: Session, user: StaffUser, case_id: UUID) -> CaseDetail:
    case = _load_case(db, case_id)
    _assert_case_access(db, user, case)
    return _case_detail(case, parse_area_config(case.area))


def change_status(
    db: Session, user: StaffUser, case_id: UUID, target: CaseStatus
) -> CaseDetail:
    case = _load_case(db, case_id)
    _assert_case_access(db, user, case)
    config = parse_area_config(case.area)
    previous = case.status
    assert_transition_allowed(config, previous, target)
    case.status = target
    record_audit(
        db,
        action=AuditAction.case_status_changed,
        entity_type="case",
        entity_id=case.id,
        actor_id=user.id,
        details={
            "area_slug": case.area.slug,
            "from": previous.value,
            "to": target.value,
        },
    )
    db.commit()
    return _case_detail(case, config)


def record_visit(
    db: Session,
    user: StaffUser,
    case_id: UUID,
    *,
    scheduled_for: datetime | None,
    notes: str | None,
) -> CaseDetail:
    case = _load_case(db, case_id)
    _assert_case_access(db, user, case)
    config = parse_area_config(case.area)
    record_audit(
        db,
        action=AuditAction.visit_recorded,
        entity_type="case",
        entity_id=case.id,
        actor_id=user.id,
        details={
            "area_slug": case.area.slug,
            "scheduled_for": scheduled_for.isoformat() if scheduled_for else None,
            "notes": notes,
        },
    )
    db.commit()
    return _case_detail(case, config)


def confirm_escalation(
    db: Session, user: StaffUser, case_id: UUID, *, note: str | None
) -> CaseDetail:
    case = _load_case(db, case_id)
    _assert_case_access(db, user, case)
    config = parse_area_config(case.area)
    if config.escalation is None:
        raise CaseConflictError("El área no define escalamiento")
    if not _pending_escalation(case):
        raise CaseConflictError("No hay una sugerencia de escalamiento pendiente")

    case.events.append(
        CaseEvent(
            case_id=case.id,
            event_type=CaseEventType.escalation_confirmed,
            public_message="La sugerencia de escalamiento fue revisada por el equipo.",
        )
    )
    record_audit(
        db,
        action=AuditAction.escalation_confirmed,
        entity_type="case",
        entity_id=case.id,
        actor_id=user.id,
        details={
            "area_slug": case.area.slug,
            "requires_human_confirmation": True,
            "note": note,
        },
    )
    db.commit()
    return _case_detail(case, config)


def reveal_contact(db: Session, user: StaffUser, report_id: UUID) -> str:
    report = db.get(Report, report_id)
    if report is None:
        raise ContactNotAvailableError("Denuncia no encontrada")
    case = db.get(Case, report.case_id)
    if case is None:
        raise ContactNotAvailableError("Caso no encontrado")
    _assert_case_access(db, user, case)

    config = parse_area_config(case.area)
    if user.role not in config.privacy.allowed_roles:
        raise _case_access_denied(db, user, case, reason="contact_role")
    if report.contact is None:
        raise ContactNotAvailableError("La denuncia no tiene contacto")

    contact = decrypt_contact(report.contact.contact_encrypted)
    record_audit(
        db,
        action=AuditAction.contact_revealed,
        entity_type="report",
        entity_id=report.id,
        actor_id=user.id,
        details={"area_slug": case.area.slug, "case_id": str(case.id)},
    )
    db.commit()
    return contact
