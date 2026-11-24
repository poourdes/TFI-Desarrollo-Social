"""reporting schema

Revision ID: a148dfeb064b
Revises:
Create Date: 2026-11-24 04:30:15.401589

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a148dfeb064b"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("case_number", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            sa.Enum("open", "in_review", "closed", name="case_status"),
            nullable=False,
        ),
        sa.Column("grouping_key_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_number"),
    )
    with op.batch_alter_table("cases", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_cases_grouping_key_hash"),
            ["grouping_key_hash"],
            unique=False,
        )

    op.create_table(
        "case_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum("report_received", "report_linked", name="case_event_type"),
            nullable=False,
        ),
        sa.Column("public_message", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("case_events", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_case_events_case_id"), ["case_id"], unique=False
        )

    op.create_table(
        "reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tracking_code_hash", sa.String(length=64), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column(
            "category",
            sa.Enum("abuse", "neglect", "abandonment", "other", name="report_category"),
            nullable=False,
        ),
        sa.Column("incident_date", sa.Date(), nullable=True),
        sa.Column("affected_name", sa.String(length=200), nullable=False),
        sa.Column(
            "affected_age_range",
            sa.Enum(
                "range_60_69",
                "range_70_79",
                "range_80_plus",
                "unknown",
                name="age_range",
            ),
            nullable=True,
        ),
        sa.Column("locality", sa.String(length=120), nullable=False),
        sa.Column("address", sa.String(length=256), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("grouping_key_hash", sa.String(length=64), nullable=True),
        sa.Column("contact_encrypted", sa.LargeBinary(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("received", "linked", "in_review", "closed", name="report_status"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_reports_case_id"), ["case_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_reports_grouping_key_hash"),
            ["grouping_key_hash"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_reports_tracking_code_hash"),
            ["tracking_code_hash"],
            unique=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_reports_tracking_code_hash"))
        batch_op.drop_index(batch_op.f("ix_reports_grouping_key_hash"))
        batch_op.drop_index(batch_op.f("ix_reports_case_id"))

    op.drop_table("reports")
    with op.batch_alter_table("case_events", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_case_events_case_id"))

    op.drop_table("case_events")
    with op.batch_alter_table("cases", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_cases_grouping_key_hash"))

    op.drop_table("cases")

    bind = op.get_bind()
    for enum in (
        sa.Enum("open", "in_review", "closed", name="case_status"),
        sa.Enum("report_received", "report_linked", name="case_event_type"),
        sa.Enum("abuse", "neglect", "abandonment", "other", name="report_category"),
        sa.Enum(
            "range_60_69",
            "range_70_79",
            "range_80_plus",
            "unknown",
            name="age_range",
        ),
        sa.Enum("received", "linked", "in_review", "closed", name="report_status"),
    ):
        enum.drop(bind, checkfirst=True)
