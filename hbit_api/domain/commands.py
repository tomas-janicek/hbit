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
    email: EmailStr
    name: str | None
    password: SecretStr
    is_superuser: bool = False


class UpdateUser(Command):
    id: int
    email: EmailStr | None = None
    name: str | None = None


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
