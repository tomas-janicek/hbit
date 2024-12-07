import typing

from pydantic import BaseModel, Field, SecretStr

if typing.TYPE_CHECKING:
    from hbit_api.domain import model


class UserDto(BaseModel):
    id: int
    email: str
    full_name: str | None
    is_active: bool
    is_superuser: bool

    @classmethod
    def from_user(cls, user: "model.User") -> typing.Self:
        return cls(
            id=user.id,  # type: ignore
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )


class UsersPublic(BaseModel):
    data: list[UserDto]
    count: int


class UserUpdateDto(BaseModel):
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str


class UpdatePassword(BaseModel):
    current_password: SecretStr
    new_password: SecretStr = Field(min_length=8, max_length=40)
