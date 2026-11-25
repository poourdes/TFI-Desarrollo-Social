from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import CaseEventType, CaseStatus, ReportStatus
from app.services.tracking_code import TRACKING_CODE_PATTERN


class ReportCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    situation_type: str | None = Field(default=None, min_length=2, max_length=64)
    incident_date: date | None = None
    affected_name: str | None = Field(default=None, min_length=2, max_length=200)
    affected_initials: str | None = Field(default=None, min_length=1, max_length=10)
    age_range: str | None = Field(default=None, max_length=32)
    locality: str | None = Field(default=None, min_length=2, max_length=120)
    address: str | None = Field(default=None, min_length=3, max_length=256)
    description: str | None = Field(default=None, min_length=20, max_length=4000)
    relationship_to_victim: str | None = Field(default=None, max_length=64)
    contact: str | None = Field(default=None, min_length=3, max_length=256)
    captcha_token: str | None = Field(default=None, min_length=1, max_length=4096)

    @field_validator(
        "situation_type",
        "affected_name",
        "affected_initials",
        "locality",
        "address",
        "description",
        "relationship_to_victim",
        "contact",
        "captcha_token",
    )
    @classmethod
    def reject_blank_text(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("El campo no puede estar vacío")
        return value

    @field_validator("incident_date")
    @classmethod
    def reject_future_date(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("La fecha del hecho no puede ser futura")
        return value


class ReportCreatedResponse(BaseModel):
    tracking_code: str
    case_number: str
    area_slug: str
    status: ReportStatus
    created_at: datetime


class TrackingRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    tracking_code: str = Field(pattern=TRACKING_CODE_PATTERN)

    @field_validator("tracking_code", mode="before")
    @classmethod
    def uppercase_code(cls, value: str) -> str:
        return value.strip().upper()


class TrackingEvent(BaseModel):
    event_type: CaseEventType
    message: str
    created_at: datetime


class TrackingStatusResponse(BaseModel):
    case_number: str
    case_status: CaseStatus
    created_at: datetime
    timeline: list[TrackingEvent]
