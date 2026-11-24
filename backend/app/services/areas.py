from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.areas import EMERGENCY_LINES, PUBLIC_NOTICE
from app.models import Area
from app.schemas.area import (
    EmergencyLine,
    FormFieldPublic,
    PublicArea,
    PublicAreasResponse,
    PublicForm,
)
from app.schemas.area_config import AreaConfig, Choice
from app.schemas.report import ReportCreate


class AreaLookupError(ValueError):
    pass


class FormValidationError(ValueError):
    pass


def get_active_area(db: Session, slug: str) -> Area:
    area = db.scalar(select(Area).where(Area.slug == slug, Area.activa.is_(True)))
    if area is None:
        raise AreaLookupError(f"Área no disponible: {slug}")
    return area


def parse_area_config(area: Area) -> AreaConfig:
    return AreaConfig.model_validate(area.configuracion or {})


def validate_form(config: AreaConfig, payload: ReportCreate) -> None:
    errors: list[str] = []
    for name in payload.model_fields_set:
        field = config.form.fields.get(name)
        if field is None or not field.visible:
            errors.append(f"{name}: campo no disponible para esta área")

    if errors:
        raise FormValidationError("; ".join(errors))

    for name, field in config.form.fields.items():
        value = getattr(payload, name, None)
        if field.required and (
            value is None or (isinstance(value, str) and not value.strip())
        ):
            errors.append(f"{name}: campo obligatorio")

    if errors:
        raise FormValidationError("; ".join(errors))

    choices_by_field: dict[str, list[Choice]] = {
        "situation_type": config.form.situation_types,
        "relationship_to_victim": config.form.relationship_options,
    }
    for name, field in config.form.fields.items():
        if field.visible and field.choices is not None:
            choices_by_field[name] = field.choices

    for name, choices in choices_by_field.items():
        value = getattr(payload, name, None)
        if value is not None and value not in {choice.value for choice in choices}:
            errors.append(f"{name}: opción no válida")

    if errors:
        raise FormValidationError("; ".join(errors))


def build_public_areas(db: Session) -> PublicAreasResponse:
    areas = db.scalars(
        select(Area).where(Area.activa.is_(True)).order_by(Area.nombre)
    ).all()
    public_areas: list[PublicArea] = []
    for area in areas:
        config = parse_area_config(area)
        public_areas.append(
            PublicArea(
                id=area.id,
                nombre=area.nombre,
                slug=area.slug,
                descripcion=area.descripcion,
                anonymity=config.privacy.anonymity,
                form=PublicForm(
                    situation_types=config.form.situation_types,
                    relationship_options=config.form.relationship_options,
                    fields=[
                        FormFieldPublic(
                            key=name,
                            label=field.label,
                            required=field.required,
                            choices=field.choices,
                        )
                        for name, field in config.form.fields.items()
                        if field.visible
                    ],
                ),
            )
        )
    return PublicAreasResponse(
        notice=PUBLIC_NOTICE,
        emergency_lines=[
            EmergencyLine(numero=line["numero"], etiqueta=line["etiqueta"])
            for line in EMERGENCY_LINES
        ],
        areas=public_areas,
    )
