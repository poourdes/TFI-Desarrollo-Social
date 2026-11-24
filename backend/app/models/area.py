import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import staff_user_areas
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.staff_user import StaffUser


class Area(TimestampMixin, Base):
    __tablename__ = "areas"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    slug: Mapped[str] = mapped_column(
        sa.String(64), unique=True, nullable=False, index=True
    )
    activa: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    configuracion: Mapped[dict] = mapped_column(
        sa.JSON().with_variant(JSONB(), "postgresql"),
        default=dict,
        nullable=False,
    )

    cases: Mapped[list["Case"]] = relationship(back_populates="area")
    staff_users: Mapped[list["StaffUser"]] = relationship(
        secondary=staff_user_areas, back_populates="areas"
    )
