import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CaseStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.area import Area
    from app.models.case_event import CaseEvent
    from app.models.report import Report


class Case(TimestampMixin, Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    case_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    area_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("areas.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, name="case_status"), default=CaseStatus.open, nullable=False
    )
    grouping_key_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )

    area: Mapped["Area"] = relationship(back_populates="cases")
    reports: Mapped[list["Report"]] = relationship(back_populates="case")
    events: Mapped[list["CaseEvent"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
