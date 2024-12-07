import typing

import svcs
from pydantic import BaseModel


class Event(BaseModel):
    pass


class EventHandler(typing.Protocol):
    def __call__(self, event: typing.Any, services: svcs.Container) -> None: ...


EventHandlersConfig = dict[type[Event], typing.Sequence[EventHandler]]


class Notify(Event):
    message: str


class NotifyNewAccount(Event):
    email: str


class NotifyRecoverPassword(Event):
    email: str


class TestNotify(Event):
    email: str
