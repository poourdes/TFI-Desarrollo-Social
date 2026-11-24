from uuid import UUID

from pydantic import BaseModel

from app.schemas.area_config import AnonymityLevel, Choice


class FormFieldPublic(BaseModel):
    key: str
    label: str
    required: bool
    choices: list[Choice] | None = None


class PublicForm(BaseModel):
    situation_types: list[Choice]
    relationship_options: list[Choice]
    fields: list[FormFieldPublic]


class PublicArea(BaseModel):
    id: UUID
    nombre: str
    slug: str
    descripcion: str | None
    anonymity: AnonymityLevel
    form: PublicForm


class EmergencyLine(BaseModel):
    numero: str
    etiqueta: str


class PublicAreasResponse(BaseModel):
    notice: str
    emergency_lines: list[EmergencyLine]
    areas: list[PublicArea]
