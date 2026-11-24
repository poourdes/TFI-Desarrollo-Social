from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import StaffRole


class LoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=256)


class UserArea(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    nombre: str


class AuthenticatedUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    role: StaffRole
    areas: list[UserArea]
