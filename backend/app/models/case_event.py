import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CaseEventType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.case import Case


class CaseEvent(TimestampMixin, Base):
    __tablename__ = "case_events"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[CaseEventType] = mapped_column(
        Enum(CaseEventType, name="case_event_type"), nullable=False
    )
    public_message: Mapped[str] = mapped_column(String(200), nullable=False)

    case: Mapped["Case"] = relationship(back_populates="events")
