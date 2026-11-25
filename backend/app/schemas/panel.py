from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CaseEventType, CaseStatus, ReportStatus, StaffRole


class CaseListItem(BaseModel):
    id: UUID
    case_number: str
    area_slug: str
    area_name: str
    status: CaseStatus
    report_count: int
    created_at: datetime


class PanelReport(BaseModel):
    id: UUID
    situation_type: str
    locality: str
    address: str | None
    description: str
    status: ReportStatus
    incident_date: date | None
    created_at: datetime
    has_contact: bool


class PanelEvent(BaseModel):
    event_type: CaseEventType
    message: str
    created_at: datetime


class CaseDetail(BaseModel):
    id: UUID
    case_number: str
    area_slug: str
    area_name: str
    status: CaseStatus
    created_at: datetime
    allowed_transitions: list[CaseStatus]
    pending_escalation: bool
    reports: list[PanelReport]
    timeline: list[PanelEvent]


class TransitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: CaseStatus


class VisitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scheduled_for: datetime | None = None
    notes: str | None = Field(default=None, max_length=500)


class EscalationConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confirm: Literal[True]
    note: str | None = Field(default=None, max_length=500)


class ContactResponse(BaseModel):
    report_id: UUID
    contact: str


class AdminUserCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=256)
    full_name: str = Field(min_length=2, max_length=200)
    role: StaffRole
    area_slugs: list[str] = Field(min_length=1)
    active: bool = True


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    role: StaffRole
    active: bool
    areas: list[dict[str, str]]
