from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import CaseStatus, StaffRole

KNOWN_FORM_FIELDS = frozenset(
    {
        "situation_type",
        "incident_date",
        "affected_name",
        "affected_initials",
        "age_range",
        "locality",
        "address",
        "description",
        "relationship_to_victim",
        "contact",
    }
)


class AnonymityLevel(StrEnum):
    standard = "standard"
    reinforced = "reinforced"


class PanelAccess(StrEnum):
    standard = "standard"
    restricted = "restricted"


class Choice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: str = Field(min_length=1, max_length=64)
    label: str = Field(min_length=1, max_length=120)


class FormFieldConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=120)
    visible: bool = True
    required: bool = False
    choices: list[Choice] | None = None


def _default_choices() -> list[Choice]:
    return [Choice(value="other", label="Otra situación")]


def _default_fields() -> dict[str, "FormFieldConfig"]:
    return {
        "situation_type": FormFieldConfig(
            label="Tipo de situación", required=True, choices=_default_choices()
        ),
        "description": FormFieldConfig(label="Relato de los hechos", required=True),
        "locality": FormFieldConfig(label="Localidad", required=True),
        "contact": FormFieldConfig(label="Contacto (opcional)"),
    }


def _unique_values(choices: list[Choice]) -> list[Choice]:
    values = [choice.value for choice in choices]
    if len(values) != len(set(values)):
        raise ValueError("Las opciones no pueden repetir valores")
    return choices


class FormConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    situation_types: list[Choice] = Field(
        default_factory=_default_choices, min_length=1
    )
    relationship_options: list[Choice] = Field(default_factory=list)
    fields: dict[str, FormFieldConfig] = Field(default_factory=_default_fields)

    @field_validator("situation_types", "relationship_options")
    @classmethod
    def check_choices(cls, value: list[Choice]) -> list[Choice]:
        return _unique_values(value)

    @field_validator("fields")
    @classmethod
    def check_fields(
        cls, value: dict[str, FormFieldConfig]
    ) -> dict[str, FormFieldConfig]:
        unknown = sorted(set(value) - KNOWN_FORM_FIELDS)
        if unknown:
            raise ValueError(f"Campos de formulario desconocidos: {', '.join(unknown)}")
        for name, field in value.items():
            if field.required and not field.visible:
                raise ValueError(f"{name} no puede ser obligatorio y no visible")
            if field.choices is not None:
                _unique_values(field.choices)
        for name in ("situation_type", "description", "locality"):
            if name not in value or not value[name].required:
                raise ValueError(f"{name} debe ser un campo obligatorio")
        return value


def _default_transitions() -> dict[CaseStatus, list[CaseStatus]]:
    return {
        CaseStatus.open: [CaseStatus.in_review, CaseStatus.closed],
        CaseStatus.in_review: [CaseStatus.open, CaseStatus.closed],
        CaseStatus.closed: [],
    }


class WorkflowConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    initial_status: CaseStatus = CaseStatus.open
    transitions: dict[CaseStatus, list[CaseStatus]] = Field(
        default_factory=_default_transitions
    )

    @field_validator("transitions")
    @classmethod
    def check_transitions(
        cls, value: dict[CaseStatus, list[CaseStatus]]
    ) -> dict[CaseStatus, list[CaseStatus]]:
        for source, targets in value.items():
            if source in targets:
                raise ValueError("Un estado no puede transicionar a sí mismo")
        return value


class EscalationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    visit_after_reports: int | None = Field(default=None, ge=1)
    alert_threshold: int | None = Field(default=None, ge=1)
    alert_action: str = "suggest_police"
    requires_human_confirmation: bool = True

    @field_validator("alert_action")
    @classmethod
    def check_alert_action(cls, value: str) -> str:
        if value != "suggest_police":
            raise ValueError("La única acción automática permitida es sugerir policía")
        return value

    @field_validator("requires_human_confirmation")
    @classmethod
    def confirmation_is_mandatory(cls, value: bool) -> bool:
        if not value:
            raise ValueError("El escalamiento siempre requiere confirmación humana")
        return value

    @model_validator(mode="after")
    def has_threshold(self) -> Self:
        if self.visit_after_reports is None and self.alert_threshold is None:
            raise ValueError(
                "La configuración de escalamiento necesita al menos un umbral"
            )
        return self


class PrivacyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    anonymity: AnonymityLevel = AnonymityLevel.standard
    panel_access: PanelAccess = PanelAccess.standard
    allowed_roles: list[StaffRole] = Field(default_factory=lambda: list(StaffRole))

    @model_validator(mode="after")
    def check_restricted_roles(self) -> Self:
        if (
            self.panel_access is PanelAccess.restricted
            and StaffRole.social_worker in self.allowed_roles
        ):
            raise ValueError("El acceso restringido excluye al rol trabajador_social")
        return self


class AreaConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    form: FormConfig = Field(default_factory=FormConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)
    escalation: EscalationConfig | None = None
    privacy: PrivacyConfig = Field(default_factory=PrivacyConfig)
