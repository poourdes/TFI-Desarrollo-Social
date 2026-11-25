"""fase 2 panel enums

Revision ID: c4e8b1a2d760
Revises: f3b1c7d9e2a4
Create Date: 2026-11-24 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c4e8b1a2d760"
down_revision: str | Sequence[str] | None = "f3b1c7d9e2a4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_AUDIT_OLD = sa.Enum(
    "report_created",
    "escalation_suggested",
    "case_status_changed",
    "area_access_denied",
    name="audit_action",
)
_AUDIT_NEW = sa.Enum(
    "report_created",
    "escalation_suggested",
    "escalation_confirmed",
    "case_status_changed",
    "area_access_denied",
    "visit_recorded",
    "contact_revealed",
    name="audit_action",
)
_EVENT_OLD = sa.Enum(
    "report_received",
    "report_linked",
    "visit_due",
    "escalation_suggested",
    name="case_event_type",
)
_EVENT_NEW = sa.Enum(
    "report_received",
    "report_linked",
    "visit_due",
    "escalation_suggested",
    "escalation_confirmed",
    name="case_event_type",
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for value in ("escalation_confirmed", "visit_recorded", "contact_revealed"):
            op.execute(f"ALTER TYPE audit_action ADD VALUE IF NOT EXISTS '{value}'")
        op.execute(
            "ALTER TYPE case_event_type ADD VALUE IF NOT EXISTS 'escalation_confirmed'"
        )
    else:
        with op.batch_alter_table("audit_logs", schema=None) as batch_op:
            batch_op.alter_column(
                "action",
                existing_type=_AUDIT_OLD,
                type_=_AUDIT_NEW,
                existing_nullable=False,
            )
        with op.batch_alter_table("case_events", schema=None) as batch_op:
            batch_op.alter_column(
                "event_type",
                existing_type=_EVENT_OLD,
                type_=_EVENT_NEW,
                existing_nullable=False,
            )


def downgrade() -> None:
    bind = op.get_bind()
    op.execute(
        sa.text(
            "DELETE FROM audit_logs WHERE action IN "
            "('escalation_confirmed', 'visit_recorded', 'contact_revealed')"
        )
    )
    op.execute(
        sa.text("DELETE FROM case_events WHERE event_type = 'escalation_confirmed'")
    )

    if bind.dialect.name == "postgresql":
        op.execute(
            "CREATE TYPE audit_action_old AS ENUM "
            "('report_created', 'escalation_suggested', 'case_status_changed', "
            "'area_access_denied')"
        )
        op.execute(
            "ALTER TABLE audit_logs ALTER COLUMN action TYPE audit_action_old "
            "USING action::text::audit_action_old"
        )
        op.execute("DROP TYPE audit_action")
        op.execute("ALTER TYPE audit_action_old RENAME TO audit_action")

        op.execute(
            "CREATE TYPE case_event_type_old AS ENUM "
            "('report_received', 'report_linked', 'visit_due', "
            "'escalation_suggested')"
        )
        op.execute(
            "ALTER TABLE case_events ALTER COLUMN event_type "
            "TYPE case_event_type_old USING event_type::text::case_event_type_old"
        )
        op.execute("DROP TYPE case_event_type")
        op.execute("ALTER TYPE case_event_type_old RENAME TO case_event_type")
    else:
        with op.batch_alter_table("audit_logs", schema=None) as batch_op:
            batch_op.alter_column(
                "action",
                existing_type=_AUDIT_NEW,
                type_=_AUDIT_OLD,
                existing_nullable=False,
            )
        with op.batch_alter_table("case_events", schema=None) as batch_op:
            batch_op.alter_column(
                "event_type",
                existing_type=_EVENT_NEW,
                type_=_EVENT_OLD,
                existing_nullable=False,
            )
