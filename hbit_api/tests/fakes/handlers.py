import typing

import svcs

from hbit_api.domain import commands, events, models
from hbit_api.service_layer import messagebus
from hbit_api.tests.fakes import unit_of_work

ResponseType = typing.Any
FakeRecorder = list[tuple[messagebus.Message, ResponseType]]


class BusException(Exception): ...


############
# Messages #
############


class FakeCommand(commands.Command):
    message: str


class FakeEvent(events.Event):
    message: str


class FakeCreateAndEvoke(commands.Command):
    name: str


class FakeCommandRaising(commands.Command):
    exc_text: str


class FakeEventRaising(events.Event):
    exc_text: str


class MissingMessage: ...


############
# Handlers #
############


def fake_event_handler(event: FakeEvent, services: svcs.Container) -> None:
    recorder = services.get(FakeRecorder)

    recorder.append((event, None))


def fake_command_handler(cmd: FakeCommand, services: svcs.Container) -> str:
    recorder = services.get(FakeRecorder)

    response = "command-response"
    recorder.append((cmd, response))
    return response


def fake_create_and_evoke(cmd: FakeCreateAndEvoke, services: svcs.Container) -> int:
    uow = services.get(unit_of_work.UnitOfWork)
    recorder = services.get(FakeRecorder)

    manufacturer = models.Manufacturer(name=cmd.name)
    with uow:
        uow.manufacturers.add(manufacturer)
    fake_event = FakeEvent(message="event-after-command")
    manufacturer.events.append(fake_event)
    recorder.append((cmd, 0))
    return 0


def fake_command_raising(cmd: FakeCommandRaising, services: svcs.Container) -> None:
    raise BusException(cmd.exc_text)


def fake_event_raising(event: FakeEventRaising, services: svcs.Container) -> None:
    raise BusException(event.exc_text)


FAKE_EVENT_HANDLERS: events.EventHandlersConfig = {
    FakeEvent: (fake_event_handler,),
    FakeEventRaising: (fake_event_raising,),
}
FAKE_COMMAND_HANDLERS: commands.CommandHandlerConfig = {
    FakeCommand: fake_command_handler,
    FakeCreateAndEvoke: fake_create_and_evoke,
    FakeCommandRaising: fake_command_raising,
}
