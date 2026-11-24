"""multi area scope

Revision ID: f3b1c7d9e2a4
Revises: a148dfeb064b
Create Date: 2026-11-24 06:00:00.000000

"""

from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4, uuid5

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision: str = "f3b1c7d9e2a4"
down_revision: str | Sequence[str] | None = "a148dfeb064b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_AREA_NAMESPACE = UUID("6f1b6f6a-7c25-4f2e-9f9a-3b2f0c5d1e40")
_ADULTOS_ID = uuid5(_AREA_NAMESPACE, "adultos-mayores")

_ADULTOS_CONFIG = {
    "form": {
        "situation_types": [
            {"value": "abuse", "label": "Maltrato físico o psicológico"},
            {"value": "neglect", "label": "Negligencia en los cuidados"},
            {"value": "abandonment", "label": "Abandono"},
            {"value": "other", "label": "Otra situación"},
        ],
        "relationship_options": [
            {"value": "family", "label": "Familiar"},
            {"value": "caregiver", "label": "Cuidador/a"},
            {"value": "neighbor", "label": "Vecino/a"},
            {"value": "health_worker", "label": "Profesional de salud"},
            {"value": "other", "label": "Otra relación"},
        ],
        "fields": {
            "situation_type": {
                "label": "Tipo de situación",
                "visible": True,
                "required": True,
            },
            "incident_date": {
                "label": "Fecha del hecho",
                "visible": True,
                "required": False,
            },
            "affected_name": {
                "label": "Nombre de la persona afectada",
                "visible": True,
                "required": True,
            },
            "locality": {"label": "Localidad", "visible": True, "required": True},
            "address": {"label": "Dirección", "visible": True, "required": False},
            "description": {
                "label": "Relato de los hechos",
                "visible": True,
                "required": True,
            },
            "relationship_to_victim": {
                "label": "Relación con la persona afectada",
                "visible": True,
                "required": False,
            },
            "contact": {
                "label": "Contacto (opcional)",
                "visible": True,
                "required": False,
            },
            "age_range": {
                "label": "Rango de edad",
                "visible": True,
                "required": True,
                "choices": [
                    {"value": "range_60_69", "label": "60 a 69 años"},
                    {"value": "range_70_79", "label": "70 a 79 años"},
                    {"value": "range_80_plus", "label": "80 años o más"},
                    {"value": "unknown", "label": "Edad desconocida"},
                ],
            },
        },
    },
    "workflow": {
        "initial_status": "open",
        "transitions": {
            "open": ["in_review", "closed"],
            "in_review": ["open", "closed"],
            "closed": [],
        },
    },
    "escalation": {
        "visit_after_reports": 1,
        "alert_threshold": 3,
        "alert_action": "suggest_police",
        "requires_human_confirmation": True,
    },
    "privacy": {
        "anonymity": "standard",
        "panel_access": "standard",
        "allowed_roles": ["admin", "coordinador", "trabajador_social"],
    },
}

_JSON = sa.JSON().with_variant(JSONB(), "postgresql")
_EVENT_ENUM_OLD = sa.Enum("report_received", "report_linked", name="case_event_type")
_EVENT_ENUM_NEW = sa.Enum(
    "report_received",
    "report_linked",
    "visit_due",
    "escalation_suggested",
    name="case_event_type",
)


def _areas_table() -> sa.Table:
    return sa.table(
        "areas",
        sa.column("id", sa.Uuid()),
        sa.column("nombre", sa.String()),
        sa.column("slug", sa.String()),
        sa.column("activa", sa.Boolean()),
        sa.column("descripcion", sa.Text()),
        sa.column("configuracion", _JSON),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )


def _copy_contacts(direction: str) -> None:
    bind = op.get_bind()
    if direction == "forward":
        source = "reports"
        target = "report_contacts"
    else:
        source = "report_contacts"
        target = "reports"
    rows = (
        bind.execute(
            sa.text(
                f"SELECT id, contact_encrypted FROM {source} "
                "WHERE contact_encrypted IS NOT NULL"
            )
        )
        .mappings()
        .all()
    )
    now = datetime.now(UTC)
    for row in rows:
        bind.execute(
            sa.text(
                f"INSERT INTO {target} "
                "(id, report_id, contact_encrypted, created_at, updated_at) "
                "VALUES (:id, :report_id, :contact_encrypted, :created_at, :updated_at)"
            ),
            {
                "id": uuid4() if direction == "forward" else row["id"],
                "report_id": row["id"],
                "contact_encrypted": row["contact_encrypted"],
                "created_at": now,
                "updated_at": now,
            },
        )


def upgrade() -> None:
    bind = op.get_bind()
    now = datetime.now(UTC)

    op.create_table(
        "areas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("configuracion", _JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("areas", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_areas_slug"), ["slug"], unique=True)
    op.bulk_insert(
        _areas_table(),
        [
            {
                "id": _ADULTOS_ID,
                "nombre": "Adultos mayores",
                "slug": "adultos-mayores",
                "activa": True,
                "descripcion": (
                    "Denuncias sobre maltrato, negligencia o abandono "
                    "de personas mayores."
                ),
                "configuracion": _ADULTOS_CONFIG,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )

    with op.batch_alter_table("cases", schema=None) as batch_op:
        batch_op.add_column(sa.Column("area_id", sa.Uuid(), nullable=True))
        batch_op.create_index(batch_op.f("ix_cases_area_id"), ["area_id"], unique=False)
    op.execute(
        sa.text("UPDATE cases SET area_id = :area_id").bindparams(
            sa.bindparam("area_id", _ADULTOS_ID, type_=sa.Uuid())
        )
    )
    with op.batch_alter_table("cases", schema=None) as batch_op:
        batch_op.alter_column("area_id", existing_type=sa.Uuid(), nullable=False)
        batch_op.create_foreign_key(
            "fk_cases_area_id", "areas", ["area_id"], ["id"], ondelete="RESTRICT"
        )

    op.create_table(
        "report_contacts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("report_id", sa.Uuid(), nullable=False),
        sa.Column("contact_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["report_id"], ["reports.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("report_contacts", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_report_contacts_report_id"), ["report_id"], unique=True
        )
    _copy_contacts("forward")

    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("situation_type", sa.String(length=64), nullable=True)
        )
        batch_op.add_column(
            sa.Column("affected_initials", sa.String(length=10), nullable=True)
        )
        batch_op.add_column(sa.Column("age_range", sa.String(length=32), nullable=True))
        batch_op.add_column(
            sa.Column("relationship_to_victim", sa.String(length=64), nullable=True)
        )
        batch_op.alter_column(
            "affected_name", existing_type=sa.String(200), nullable=True
        )
        batch_op.drop_column("contact_encrypted")
    op.execute(
        sa.text(
            "UPDATE reports SET situation_type = category, "
            "age_range = affected_age_range"
        )
    )
    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.alter_column(
            "situation_type", existing_type=sa.String(64), nullable=False
        )
        batch_op.drop_column("category")
        batch_op.drop_column("affected_age_range")

    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE case_event_type ADD VALUE IF NOT EXISTS 'visit_due'")
        op.execute(
            "ALTER TYPE case_event_type ADD VALUE IF NOT EXISTS 'escalation_suggested'"
        )
    else:
        with op.batch_alter_table("case_events", schema=None) as batch_op:
            batch_op.alter_column(
                "event_type",
                existing_type=_EVENT_ENUM_OLD,
                type_=_EVENT_ENUM_NEW,
                existing_nullable=False,
            )

    op.create_table(
        "staff_users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "coordinador", "trabajador_social", name="staff_role"),
            nullable=False,
        ),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("staff_users", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_staff_users_email"), ["email"], unique=True
        )

    op.create_table(
        "staff_user_areas",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("area_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["areas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["staff_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "area_id"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column(
            "action",
            sa.Enum(
                "report_created",
                "escalation_suggested",
                "case_status_changed",
                "area_access_denied",
                name="audit_action",
            ),
            nullable=False,
        ),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=True),
        sa.Column("details", _JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["staff_users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("audit_logs", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_audit_logs_actor_id"), ["actor_id"], unique=False
        )

    if bind.dialect.name == "postgresql":
        sa.Enum(
            "abuse", "neglect", "abandonment", "other", name="report_category"
        ).drop(bind, checkfirst=True)
        sa.Enum(
            "range_60_69", "range_70_79", "range_80_plus", "unknown", name="age_range"
        ).drop(bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()

    with op.batch_alter_table("audit_logs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_audit_logs_actor_id"))
    op.drop_table("audit_logs")
    op.drop_table("staff_user_areas")
    with op.batch_alter_table("staff_users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_staff_users_email"))
    op.drop_table("staff_users")

    if bind.dialect.name == "postgresql":
        op.execute(
            "CREATE TYPE case_event_type_old AS ENUM "
            "('report_received', 'report_linked')"
        )
        op.execute(
            "ALTER TABLE case_events ALTER COLUMN event_type "
            "TYPE case_event_type_old USING event_type::text::case_event_type_old"
        )
        op.execute("DROP TYPE case_event_type")
        op.execute("ALTER TYPE case_event_type_old RENAME TO case_event_type")
    else:
        with op.batch_alter_table("case_events", schema=None) as batch_op:
            batch_op.alter_column(
                "event_type",
                existing_type=_EVENT_ENUM_NEW,
                type_=_EVENT_ENUM_OLD,
                existing_nullable=False,
            )

    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "category",
                sa.Enum(
                    "abuse", "neglect", "abandonment", "other", name="report_category"
                ),
                nullable=True,
            )
        )
        batch_op.add_column(
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
            )
        )
        batch_op.add_column(
            sa.Column("contact_encrypted", sa.LargeBinary(), nullable=True)
        )
    op.execute(
        sa.text(
            "UPDATE reports SET category = CASE WHEN situation_type IN "
            "('abuse', 'neglect', 'abandonment', 'other') "
            "THEN situation_type ELSE 'other' END, "
            "affected_age_range = CASE WHEN age_range IN "
            "('range_60_69', 'range_70_79', 'range_80_plus', 'unknown') "
            "THEN age_range ELSE NULL END"
        )
    )
    _copy_contacts("backward")
    op.execute(
        sa.text(
            "UPDATE reports SET affected_name = 'Desconocido' "
            "WHERE affected_name IS NULL"
        )
    )
    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.alter_column(
            "category",
            existing_type=sa.Enum(
                "abuse", "neglect", "abandonment", "other", name="report_category"
            ),
            nullable=False,
        )
        batch_op.alter_column(
            "affected_name", existing_type=sa.String(200), nullable=False
        )
        batch_op.drop_column("relationship_to_victim")
        batch_op.drop_column("age_range")
        batch_op.drop_column("affected_initials")
        batch_op.drop_column("situation_type")

    with op.batch_alter_table("report_contacts", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_report_contacts_report_id"))
    op.drop_table("report_contacts")

    with op.batch_alter_table("cases", schema=None) as batch_op:
        batch_op.drop_constraint("fk_cases_area_id", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_cases_area_id"))
        batch_op.drop_column("area_id")

    with op.batch_alter_table("areas", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_areas_slug"))
    op.drop_table("areas")

    if bind.dialect.name == "postgresql":
        for enum in (
            sa.Enum("admin", "coordinador", "trabajador_social", name="staff_role"),
            sa.Enum(
                "report_created",
                "escalation_suggested",
                "case_status_changed",
                "area_access_denied",
                name="audit_action",
            ),
        ):
            enum.drop(bind, checkfirst=True)
