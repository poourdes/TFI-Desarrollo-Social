import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import staff_user_areas
from app.models.enums import StaffRole
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.area import Area


class StaffUser(TimestampMixin, Base):
    __tablename__ = "staff_users"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        sa.String(255), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    role: Mapped[StaffRole] = mapped_column(
        sa.Enum(
            StaffRole,
            name="staff_role",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
    )
    active: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    areas: Mapped[list["Area"]] = relationship(
        secondary=staff_user_areas, back_populates="staff_users"
    )
