import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ReportStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.report_contact import ReportContact


class Report(TimestampMixin, Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tracking_code_hash: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cases.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    situation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    incident_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    affected_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    affected_initials: Mapped[str | None] = mapped_column(String(10), nullable=True)
    age_range: Mapped[str | None] = mapped_column(String(32), nullable=True)
    locality: Mapped[str] = mapped_column(String(120), nullable=False)
    address: Mapped[str | None] = mapped_column(String(256), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    relationship_to_victim: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    grouping_key_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status"),
        default=ReportStatus.received,
        nullable=False,
    )

    case: Mapped["Case"] = relationship(back_populates="reports")
    contact: Mapped["ReportContact | None"] = relationship(
        back_populates="report", uselist=False, cascade="all, delete-orphan"
    )
