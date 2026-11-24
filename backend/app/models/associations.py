import sqlalchemy as sa

from app.db.base import Base

staff_user_areas = sa.Table(
    "staff_user_areas",
    Base.metadata,
    sa.Column(
        "user_id",
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("staff_users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "area_id",
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("areas.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
