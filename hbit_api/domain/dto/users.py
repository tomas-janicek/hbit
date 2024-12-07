import typing

from pydantic import BaseModel, EmailStr, Field, SecretStr

if typing.TYPE_CHECKING:
    from hbit_api.domain import models


class UserDto(BaseModel):
    id: int
    email: str
    name: str | None
    is_active: bool
    is_superuser: bool

    @classmethod
    def from_user(cls, user: "models.User") -> typing.Self:
        return cls(
            id=user.id,  # type: ignore
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )


class UsersPublic(BaseModel):
    data: list[UserDto]
    count: int


class CreateUserDto(BaseModel):
    email: EmailStr = Field(max_length=255)
    name: str | None = Field(default=None, max_length=255)
    password: SecretStr = Field(min_length=8, max_length=40)


class UserUpdateDto(BaseModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    name: str | None = Field(default=None, max_length=255)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str


class UpdatePassword(BaseModel):
    current_password: SecretStr
    new_password: SecretStr = Field(min_length=8, max_length=40)
