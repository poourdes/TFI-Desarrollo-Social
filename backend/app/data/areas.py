from dataclasses import dataclass
from uuid import UUID, uuid5

from sqlalchemy.orm import Session

from app.models import Area

AREA_NAMESPACE = UUID("6f1b6f6a-7c25-4f2e-9f9a-3b2f0c5d1e40")

EMERGENCY_LINES = (
    {"numero": "911", "etiqueta": "Emergencias generales"},
    {"numero": "144", "etiqueta": "Violencia de género"},
    {"numero": "102", "etiqueta": "Niñez y adolescencia"},
)

PUBLIC_NOTICE = (
    "Esta plataforma no es para emergencias. Ante un riesgo inmediato, "
    "comunicarse con las líneas de emergencia."
)


def area_id_for(slug: str) -> UUID:
    return uuid5(AREA_NAMESPACE, slug)


def _choice(value: str, label: str) -> dict[str, str]:
    return {"value": value, "label": label}


def _field(
    label: str,
    *,
    required: bool = False,
    visible: bool = True,
    choices: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    field: dict[str, object] = {
        "label": label,
        "visible": visible,
        "required": required,
    }
    if choices is not None:
        field["choices"] = choices
    return field


def _with_relationship(fields: dict[str, object]) -> dict[str, object]:
    return {
        **fields,
        "relationship_to_victim": _field("Relación con la persona afectada"),
    }


def _base_fields(
    *,
    include_name: bool = True,
    name_required: bool = False,
    include_initials: bool = False,
    age_choices: list[dict[str, str]] | None = None,
    age_required: bool = False,
) -> dict[str, object]:
    fields: dict[str, object] = {
        "situation_type": _field("Tipo de situación", required=True),
        "incident_date": _field("Fecha del hecho"),
        "locality": _field("Localidad", required=True),
        "address": _field("Dirección"),
        "description": _field("Relato de los hechos", required=True),
        "contact": _field("Contacto (opcional)"),
    }
    if include_name:
        fields["affected_name"] = _field(
            "Nombre de la persona afectada", required=name_required
        )
    if include_initials:
        fields["affected_initials"] = _field("Iniciales de la persona afectada")
    if age_choices is not None:
        fields["age_range"] = _field(
            "Rango de edad", required=age_required, choices=age_choices
        )
    return fields


def _base_config(
    *,
    situation_types: list[dict[str, str]],
    relationships: list[dict[str, str]],
    fields: dict[str, object],
) -> dict[str, object]:
    return {
        "form": {
            "situation_types": situation_types,
            "relationship_options": relationships,
            "fields": fields,
        },
        "privacy": {"anonymity": "standard", "panel_access": "standard"},
    }


ADULTOS_SITUATIONS = [
    _choice("abuse", "Maltrato físico o psicológico"),
    _choice("neglect", "Negligencia en los cuidados"),
    _choice("abandonment", "Abandono"),
    _choice("other", "Otra situación"),
]

ADULTOS_RELATIONSHIPS = [
    _choice("family", "Familiar"),
    _choice("caregiver", "Cuidador/a"),
    _choice("neighbor", "Vecino/a"),
    _choice("health_worker", "Profesional de salud"),
    _choice("other", "Otra relación"),
]

ADULTOS_AGE_RANGES = [
    _choice("range_60_69", "60 a 69 años"),
    _choice("range_70_79", "70 a 79 años"),
    _choice("range_80_plus", "80 años o más"),
    _choice("unknown", "Edad desconocida"),
]

ADULTOS_CONFIG: dict[str, object] = {
    "form": {
        "situation_types": ADULTOS_SITUATIONS,
        "relationship_options": ADULTOS_RELATIONSHIPS,
        "fields": _with_relationship(
            _base_fields(
                name_required=True,
                age_choices=ADULTOS_AGE_RANGES,
                age_required=True,
            )
        ),
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

VIOLENCIA_CONFIG = _base_config(
    situation_types=[
        _choice("physical", "Violencia física"),
        _choice("psychological", "Violencia psicológica"),
        _choice("sexual", "Violencia sexual"),
        _choice("economic", "Violencia económica"),
        _choice("other", "Otra situación"),
    ],
    relationships=[
        _choice("partner", "Pareja"),
        _choice("ex_partner", "Ex pareja"),
        _choice("family", "Familiar"),
        _choice("acquaintance", "Conocido/a"),
        _choice("other", "Otra relación"),
    ],
    fields=_with_relationship(_base_fields()),
)

NINEZ_CONFIG: dict[str, object] = {
    "form": {
        "situation_types": [
            _choice("mistreatment", "Maltrato"),
            _choice("abandonment", "Abandono"),
            _choice("violence", "Violencia"),
            _choice("rights", "Vulneración de derechos"),
            _choice("other", "Otra situación"),
        ],
        "relationship_options": [
            _choice("family", "Familiar"),
            _choice("teacher", "Docente"),
            _choice("caregiver", "Cuidador/a"),
            _choice("other", "Otra relación"),
        ],
        "fields": _with_relationship(
            _base_fields(
                include_name=False,
                include_initials=True,
                age_choices=[
                    _choice("range_0_5", "0 a 5 años"),
                    _choice("range_6_11", "6 a 11 años"),
                    _choice("range_12_17", "12 a 17 años"),
                    _choice("unknown", "Edad desconocida"),
                ],
            )
        ),
    },
    "privacy": {
        "anonymity": "reinforced",
        "panel_access": "restricted",
        "allowed_roles": ["admin", "coordinador"],
    },
}

DIVERSIDAD_CONFIG: dict[str, object] = {
    "form": {
        "situation_types": [
            _choice("discrimination", "Discriminación"),
            _choice("violence", "Violencia"),
            _choice("rights", "Negación de derechos"),
            _choice("other", "Otra situación"),
        ],
        "relationship_options": [
            _choice("partner", "Pareja"),
            _choice("family", "Familiar"),
            _choice("acquaintance", "Conocido/a"),
            _choice("other", "Otra relación"),
        ],
        "fields": _with_relationship(_base_fields(include_name=False)),
    },
    "privacy": {
        "anonymity": "reinforced",
        "panel_access": "restricted",
        "allowed_roles": ["admin", "coordinador"],
    },
}

ABUSO_LABORAL_CONFIG = _base_config(
    situation_types=[
        _choice("harassment", "Acoso laboral"),
        _choice("exploitation", "Explotación"),
        _choice("dismissal", "Despido injustificado"),
        _choice("unsafe", "Condiciones peligrosas"),
        _choice("other", "Otra situación"),
    ],
    relationships=[
        _choice("employer", "Empleador/a"),
        _choice("supervisor", "Supervisor/a"),
        _choice("coworker", "Compañero/a"),
        _choice("other", "Otra relación"),
    ],
    fields=_with_relationship(_base_fields()),
)


@dataclass(frozen=True)
class AreaDefinition:
    id: UUID
    nombre: str
    slug: str
    activa: bool
    descripcion: str
    configuracion: dict[str, object]


AREA_DEFINITIONS: tuple[AreaDefinition, ...] = (
    AreaDefinition(
        id=area_id_for("adultos-mayores"),
        nombre="Adultos mayores",
        slug="adultos-mayores",
        activa=True,
        descripcion=(
            "Denuncias sobre maltrato, negligencia o abandono de personas mayores."
        ),
        configuracion=ADULTOS_CONFIG,
    ),
    AreaDefinition(
        id=area_id_for("violencia-de-genero"),
        nombre="Violencia de género",
        slug="violencia-de-genero",
        activa=True,
        descripcion="Denuncias sobre violencia por razones de género.",
        configuracion=VIOLENCIA_CONFIG,
    ),
    AreaDefinition(
        id=area_id_for("ninez-adolescencia"),
        nombre="Niñez y adolescencia",
        slug="ninez-adolescencia",
        activa=True,
        descripcion=(
            "Denuncias sobre vulneración de derechos de niñas, niños y adolescentes."
        ),
        configuracion=NINEZ_CONFIG,
    ),
    AreaDefinition(
        id=area_id_for("diversidad-genero"),
        nombre="Diversidad sexual y de género",
        slug="diversidad-genero",
        activa=True,
        descripcion=(
            "Denuncias sobre discriminación o violencia por diversidad sexual "
            "y de género."
        ),
        configuracion=DIVERSIDAD_CONFIG,
    ),
    AreaDefinition(
        id=area_id_for("abuso-laboral"),
        nombre="Abuso laboral",
        slug="abuso-laboral",
        activa=True,
        descripcion=(
            "Denuncias sobre acoso, explotación u otras situaciones laborales "
            "abusivas."
        ),
        configuracion=ABUSO_LABORAL_CONFIG,
    ),
)


def seed_areas(db: Session) -> None:
    for definition in AREA_DEFINITIONS:
        area = db.get(Area, definition.id)
        if area is None:
            area = Area(id=definition.id)
            db.add(area)
        area.nombre = definition.nombre
        area.slug = definition.slug
        area.activa = definition.activa
        area.descripcion = definition.descripcion
        area.configuracion = definition.configuracion
    db.commit()
