"""fase 3 security rbac

Revision ID: d5f2a8c1b3e4
Revises: c4e8b1a2d760
Create Date: 2026-11-25 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from cryptography.fernet import Fernet

from alembic import op
from app.core.config import settings

revision: str = "d5f2a8c1b3e4"
down_revision: str | Sequence[str] | None = "c4e8b1a2d760"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DESCRIPTION_DOMAIN = b"report-description:v1:"

_AUDIT_OLD = sa.Enum(
    "report_created",
    "escalation_suggested",
    "escalation_confirmed",
    "case_status_changed",
    "area_access_denied",
    "visit_recorded",
    "contact_revealed",
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
    "sensitive_data_revealed",
    "staff_user_created",
    name="audit_action",
)


def _fernet() -> Fernet:
    key = settings.fernet_key.strip()
    if not key:
        raise RuntimeError(
            "FERNET_KEY debe estar configurada antes de ejecutar la migración "
            "fase 3: no se puede cifrar description sin una clave Fernet válida."
        )
    try:
        return Fernet(key.encode("ascii"))
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("FERNET_KEY inválida para la migración fase 3") from exc


def upgrade() -> None:
    bind = op.get_bind()
    fernet = _fernet()

    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TYPE audit_action ADD VALUE IF NOT EXISTS 'sensitive_data_revealed'"
        )
        op.execute(
            "ALTER TYPE audit_action ADD VALUE IF NOT EXISTS 'staff_user_created'"
        )
    else:
        with op.batch_alter_table("audit_logs", schema=None) as batch_op:
            batch_op.alter_column(
                "action",
                existing_type=_AUDIT_OLD,
                type_=_AUDIT_NEW,
                existing_nullable=False,
            )

    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("description_encrypted", sa.LargeBinary(), nullable=True)
        )

    rows = bind.execute(sa.text("SELECT id, description FROM reports")).mappings().all()
    for row in rows:
        plaintext = row["description"] or ""
        token = fernet.encrypt(DESCRIPTION_DOMAIN + plaintext.encode("utf-8"))
        bind.execute(
            sa.text("UPDATE reports SET description_encrypted = :token WHERE id = :id"),
            {"token": token, "id": row["id"]},
        )

    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.alter_column(
            "description_encrypted",
            existing_type=sa.LargeBinary(),
            nullable=False,
        )
        batch_op.drop_column("description")


def downgrade() -> None:
    bind = op.get_bind()
    fernet = _fernet()

    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.add_column(sa.Column("description", sa.Text(), nullable=True))

    rows = (
        bind.execute(sa.text("SELECT id, description_encrypted FROM reports"))
        .mappings()
        .all()
    )
    for row in rows:
        token = row["description_encrypted"]
        plaintext = ""
        if token:
            decrypted = fernet.decrypt(bytes(token))
            if not decrypted.startswith(DESCRIPTION_DOMAIN):
                raise RuntimeError("Payload cifrado inválido en downgrade")
            plaintext = decrypted[len(DESCRIPTION_DOMAIN) :].decode("utf-8")
        bind.execute(
            sa.text("UPDATE reports SET description = :description WHERE id = :id"),
            {"description": plaintext, "id": row["id"]},
        )

    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.alter_column("description", existing_type=sa.Text(), nullable=False)
        batch_op.drop_column("description_encrypted")

    op.execute(
        sa.text(
            "DELETE FROM audit_logs WHERE action IN "
            "('sensitive_data_revealed', 'staff_user_created')"
        )
    )

    if bind.dialect.name == "postgresql":
        op.execute(
            "CREATE TYPE audit_action_old AS ENUM "
            "('report_created', 'escalation_suggested', 'escalation_confirmed', "
            "'case_status_changed', 'area_access_denied', 'visit_recorded', "
            "'contact_revealed')"
        )
        op.execute(
            "ALTER TABLE audit_logs ALTER COLUMN action TYPE audit_action_old "
            "USING action::text::audit_action_old"
        )
        op.execute("DROP TYPE audit_action")
        op.execute("ALTER TYPE audit_action_old RENAME TO audit_action")
    else:
        with op.batch_alter_table("audit_logs", schema=None) as batch_op:
            batch_op.alter_column(
                "action",
                existing_type=_AUDIT_NEW,
                type_=_AUDIT_OLD,
                existing_nullable=False,
            )
