from dataclasses import dataclass
from datetime import date, datetime
from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Area,
    AuditAction,
    Case,
    CaseEvent,
    CaseEventType,
    CaseStatus,
    Report,
    ReportContact,
    ReportStatus,
)
from app.schemas.area_config import AreaConfig
from app.schemas.report import ReportCreate
from app.services.areas import validate_form
from app.services.audit import record_audit
from app.services.contact import encrypt_contact
from app.services.escalation import evaluate_escalation
from app.services.grouping import build_grouping_key
from app.services.tracking_code import generate_tracking_code, hash_tracking_code


@dataclass(frozen=True)
class CreatedReport:
    report: Report
    tracking_code: str
    case_number: str


@dataclass(frozen=True)
class TrackedReport:
    case_number: str
    case_status: CaseStatus
    created_at: datetime
    timeline: list[CaseEvent]


def _next_case_number(db: Session, today: date) -> str:
    prefix = f"CASO-{today:%Y%m}-"
    last = db.scalar(
        select(Case.case_number)
        .where(Case.case_number.like(f"{prefix}%"))
        .order_by(Case.case_number.desc())
    )
    sequence = int(last[len(prefix) :]) + 1 if last else 1
    return f"{prefix}{sequence:04d}"


def _find_open_case(
    db: Session, area_id: UUID, grouping_key: str | None
) -> Case | None:
    if grouping_key is None:
        return None
    return db.scalar(
        select(Case)
        .where(
            Case.area_id == area_id,
            Case.grouping_key_hash == grouping_key,
            Case.status.in_([CaseStatus.open, CaseStatus.in_review]),
        )
        .order_by(Case.created_at.asc())
    )


def create_report(
    db: Session, area: Area, config: AreaConfig, payload: ReportCreate
) -> CreatedReport:
    validate_form(config, payload)
    tracking_code = generate_tracking_code()
    situation_type = cast(str, payload.situation_type)
    locality = cast(str, payload.locality)
    grouping_key = build_grouping_key(
        area.id, locality, payload.address, payload.affected_name
    )

    case = _find_open_case(db, area.id, grouping_key)
    is_new_case = case is None
    if case is None:
        case = Case(
            case_number=_next_case_number(db, date.today()),
            area_id=area.id,
            grouping_key_hash=grouping_key,
            status=config.workflow.initial_status,
        )
        db.add(case)
        db.flush()

    report = Report(
        tracking_code_hash=hash_tracking_code(tracking_code),
        case_id=case.id,
        situation_type=situation_type,
        incident_date=payload.incident_date,
        affected_name=payload.affected_name,
        affected_initials=payload.affected_initials,
        age_range=payload.age_range,
        locality=locality,
        address=payload.address,
        description=cast(str, payload.description),
        relationship_to_victim=payload.relationship_to_victim,
        grouping_key_hash=grouping_key,
        status=ReportStatus.received if is_new_case else ReportStatus.linked,
    )
    if payload.contact is not None:
        report.contact = ReportContact(
            contact_encrypted=encrypt_contact(payload.contact)
        )
    db.add(report)
    db.flush()

    case_events = [
        CaseEvent(
            case_id=case.id,
            event_type=(
                CaseEventType.report_received
                if is_new_case
                else CaseEventType.report_linked
            ),
            public_message=(
                "Denuncia recibida."
                if is_new_case
                else "Se asoció una nueva denuncia a este caso."
            ),
        )
    ]
    record_audit(
        db,
        action=AuditAction.report_created,
        entity_type="report",
        entity_id=report.id,
        details={"area_slug": area.slug, "linked": not is_new_case},
    )

    report_count = db.scalar(
        select(func.count()).select_from(Report).where(Report.case_id == case.id)
    )
    for suggestion in evaluate_escalation(config, report_count or 0):
        case_events.append(
            CaseEvent(
                case_id=case.id,
                event_type=suggestion.event_type,
                public_message=suggestion.public_message,
            )
        )
        record_audit(
            db,
            action=AuditAction.escalation_suggested,
            entity_type="case",
            entity_id=case.id,
            details={
                "area_slug": area.slug,
                "report_count": report_count,
                "requires_human_confirmation": True,
            },
        )

    db.add_all(case_events)
    db.commit()
    db.refresh(report)
    db.refresh(case)
    return CreatedReport(
        report=report,
        tracking_code=tracking_code,
        case_number=case.case_number,
    )


def get_tracked_report(db: Session, tracking_code: str) -> TrackedReport | None:
    code_hash = hash_tracking_code(tracking_code)
    report = db.scalar(select(Report).where(Report.tracking_code_hash == code_hash))
    if report is None:
        return None
    case = db.get(Case, report.case_id)
    if case is None:
        return None
    events = db.scalars(
        select(CaseEvent)
        .where(CaseEvent.case_id == case.id)
        .order_by(CaseEvent.created_at.asc())
    ).all()
    return TrackedReport(
        case_number=case.case_number,
        case_status=case.status,
        created_at=case.created_at,
        timeline=list(events),
    )
