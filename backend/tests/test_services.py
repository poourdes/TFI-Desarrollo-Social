from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.data.areas import area_id_for
from app.models import CaseEventType, CaseStatus, StaffRole
from app.schemas.area_config import (
    AreaConfig,
    EscalationConfig,
    PanelAccess,
    PrivacyConfig,
)
from app.schemas.report import ReportCreate
from app.services.areas import get_active_area, parse_area_config, validate_form
from app.services.contact import decrypt_contact, encrypt_contact
from app.services.escalation import evaluate_escalation
from app.services.grouping import build_grouping_key, normalize_grouping_text
from app.services.tracking_code import (
    TRACKING_CODE_RE,
    generate_tracking_code,
    hash_tracking_code,
    normalize_tracking_code,
)
from app.services.workflow import InvalidTransitionError, assert_transition_allowed


def test_tracking_codes_are_unique_and_well_formed() -> None:
    codes = {generate_tracking_code() for _ in range(50)}
    assert len(codes) == 50
    assert all(TRACKING_CODE_RE.fullmatch(code) for code in codes)


def test_tracking_code_hash_is_stable_and_normalized() -> None:
    code = generate_tracking_code()
    assert hash_tracking_code(code) == hash_tracking_code(
        normalize_tracking_code(code.lower())
    )
    assert hash_tracking_code(code) != hash_tracking_code(generate_tracking_code())


def test_grouping_text_normalization() -> None:
    assert normalize_grouping_text("  Calle SarMiento 123  ") == "calle sarmiento 123"
    assert normalize_grouping_text("María José") == "maria jose"


def test_grouping_key_requirements_and_area_scope() -> None:
    area_id = area_id_for("adultos-mayores")
    assert build_grouping_key(area_id, "Aguilares", None) is None
    first = build_grouping_key(area_id, "Aguilares", "Calle Sarmiento 123")
    second = build_grouping_key(area_id, "  aguilares ", "calle sarMiento 123")
    assert first == second
    assert first != build_grouping_key(area_id, "Aguilares", "Otra calle 45")
    assert first != build_grouping_key(uuid4(), "Aguilares", "Calle Sarmiento 123")


def test_contact_encryption_roundtrip_and_invalid_token() -> None:
    token = encrypt_contact("381 555 1234")
    assert b"381 555 1234" not in token
    assert decrypt_contact(token) == "381 555 1234"
    with pytest.raises(ValueError):
        decrypt_contact(b"token-invalido")


def test_adultos_escalation_is_config_driven(db_session: Session) -> None:
    area = get_active_area(db_session, "adultos-mayores")
    config = parse_area_config(area)
    assert config.escalation is not None
    assert config.escalation.visit_after_reports == 1
    assert config.escalation.alert_threshold == 3

    assert [item.event_type for item in evaluate_escalation(config, 1)] == [
        CaseEventType.visit_due
    ]
    assert [item.event_type for item in evaluate_escalation(config, 2)] == []
    assert [item.event_type for item in evaluate_escalation(config, 3)] == [
        CaseEventType.escalation_suggested
    ]
    assert evaluate_escalation(config, 4) == []


def test_areas_without_threshold_never_escalate(db_session: Session) -> None:
    for slug in (
        "violencia-de-genero",
        "ninez-adolescencia",
        "diversidad-genero",
        "abuso-laboral",
    ):
        config = parse_area_config(get_active_area(db_session, slug))
        assert config.escalation is None
        assert evaluate_escalation(config, 10) == []


def test_human_confirmation_cannot_be_disabled() -> None:
    with pytest.raises(ValidationError):
        EscalationConfig(
            visit_after_reports=1,
            alert_threshold=3,
            requires_human_confirmation=False,
        )


def test_workflow_transitions_come_from_config(db_session: Session) -> None:
    config = parse_area_config(get_active_area(db_session, "adultos-mayores"))
    assert_transition_allowed(config, CaseStatus.open, CaseStatus.in_review)
    with pytest.raises(InvalidTransitionError):
        assert_transition_allowed(config, CaseStatus.closed, CaseStatus.open)

    custom = AreaConfig.model_validate(
        {
            "workflow": {
                "transitions": {
                    "open": ["closed"],
                    "in_review": [],
                    "closed": ["open"],
                }
            }
        }
    )
    assert_transition_allowed(custom, CaseStatus.closed, CaseStatus.open)


def test_restricted_privacy_excludes_social_worker() -> None:
    config = PrivacyConfig(
        anonymity="reinforced",
        panel_access=PanelAccess.restricted,
        allowed_roles=[StaffRole.admin, StaffRole.coordinator],
    )
    assert config.panel_access is PanelAccess.restricted
    with pytest.raises(ValidationError):
        PrivacyConfig(
            panel_access=PanelAccess.restricted,
            allowed_roles=[StaffRole.social_worker],
        )


def test_reinforced_areas_hide_unnecessary_fields(db_session: Session) -> None:
    for slug in ("ninez-adolescencia", "diversidad-genero"):
        config = parse_area_config(get_active_area(db_session, slug))
        assert config.privacy.anonymity == "reinforced"
        assert config.privacy.panel_access is PanelAccess.restricted
        assert "affected_name" not in config.form.fields

    ninez = parse_area_config(get_active_area(db_session, "ninez-adolescencia"))
    assert "affected_initials" in ninez.form.fields
    payload = ReportCreate(
        situation_type="mistreatment",
        locality="Aguilares",
        description="Situación de vulneración de derechos con datos mínimos.",
        affected_initials="M. P.",
    )
    validate_form(ninez, payload)

    with pytest.raises(ValueError, match="affected_name"):
        validate_form(
            ninez,
            ReportCreate(
                situation_type="mistreatment",
                locality="Aguilares",
                description="Situación de vulneración de derechos con datos mínimos.",
                affected_name="María Pérez",
            ),
        )
