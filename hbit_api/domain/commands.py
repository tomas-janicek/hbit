import typing

import svcs
from pydantic import BaseModel, EmailStr, Field, SecretStr


class Command(BaseModel):
    pass


class CommandHandler(typing.Protocol):
    def __call__(self, cmd: typing.Any, services: svcs.Container) -> typing.Any: ...


CommandHandlerConfig = dict[type[Command], CommandHandler]


class CreateAuthor(Command):
    name: str


class CreateBook(Command):
    name: str


class CreateUser(Command):
    email: EmailStr = Field(max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    password: SecretStr = Field(min_length=8, max_length=40)
    is_superuser: bool = False


class UpdateUser(Command):
    id: int
    email: EmailStr | None = Field(max_length=255, default=None)


class UpdateUserPassword(Command):
    id: int
    current_password: SecretStr
    new_password: SecretStr


class LogInUser(Command):
    email: str
    password: str


class AuthenticateUser(Command):
    token: str


class RecoverUserPassword(Command):
    email: str


class ResetPassword(Command):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class DeleteUser(Command):
    id: int
