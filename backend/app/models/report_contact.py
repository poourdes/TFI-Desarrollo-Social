import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.report import Report


class ReportContact(TimestampMixin, Base):
    __tablename__ = "report_contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    report_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    contact_encrypted: Mapped[bytes] = mapped_column(sa.LargeBinary, nullable=False)

    report: Mapped["Report"] = relationship(back_populates="contact")
