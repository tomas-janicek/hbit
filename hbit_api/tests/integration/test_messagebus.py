import logging

import pytest
import svcs

from hbit_api.service_layer import messagebus
from hbit_api.tests.fakes import handlers


def test_event(services: svcs.Container) -> None:
    bus = services.get(messagebus.MessageBus)
    recorder = services.get(handlers.FakeRecorder)

    # act
    fake_event = handlers.FakeEvent(message="one-event-test")
    bus.handle(fake_event)

    # assert
    assert len(recorder) == 1
    event, response = recorder[0]
    assert event.message == fake_event.message  # type: ignore
    assert not response


def test_command(services: svcs.Container) -> None:
    bus = services.get(messagebus.MessageBus)
    recorder = services.get(handlers.FakeRecorder)

    # act
    fake_command = handlers.FakeCommand(message="one-command-test")
    bus.handle(fake_command)

    # assert
    assert len(recorder) == 1
    command, response = recorder[0]
    assert command.message == fake_command.message  # type: ignore
    assert response == "command-response"


def test_command_evoking_event(services: svcs.Container) -> None:
    bus = services.get(messagebus.MessageBus)
    recorder = services.get(handlers.FakeRecorder)

    # act
    fake_command = handlers.FakeCreateAndEvoke(name="new-manufacturer")
    bus.handle(fake_command)

    # assert
    assert len(recorder) == 2
    event, response = recorder[0]
    assert event.name == fake_command.name  # type: ignore
    assert response == 0
    # evoked event check
    event, response = recorder[1]
    assert event.message == "event-after-command"  # type: ignore
    assert not response


def test_command_raising_exception(services: svcs.Container) -> None:
    bus = services.get(messagebus.MessageBus)

    # act & assert raises
    fake_command = handlers.FakeCommandRaising(exc_text="command-error-text")
    with pytest.raises(expected_exception=handlers.BusException):
        bus.handle(fake_command)


def test_event_raising_exception(
    services: svcs.Container, caplog: pytest.LogCaptureFixture
) -> None:
    bus = services.get(messagebus.MessageBus)

    # act & assert logged
    fake_event = handlers.FakeEventRaising(exc_text="event-error-text")
    with caplog.at_level(logging.ERROR):
        bus.handle(fake_event)

    assert fake_event.exc_text in caplog.text


def test_missing_event(
    services: svcs.Container, caplog: pytest.LogCaptureFixture
) -> None:
    bus = services.get(messagebus.MessageBus)

    # act & assert raises
    with pytest.raises(expected_exception=KeyError):
        bus.handle(handlers.MissingEvent())


def test_missing_command(
    services: svcs.Container, caplog: pytest.LogCaptureFixture
) -> None:
    bus = services.get(messagebus.MessageBus)

    # act & assert raises
    with pytest.raises(expected_exception=KeyError):
        bus.handle(handlers.MissingCommand())
