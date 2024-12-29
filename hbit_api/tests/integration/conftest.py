import pytest
import svcs

from hbit_api.adapters.email_sender import BaseEmailSender
from hbit_api.service_layer import messagebus
from hbit_api.tests.fakes import email_sender, unit_of_work
from hbit_api.tests.fakes import handlers as fake_handlers


@pytest.fixture
def services() -> svcs.Container:
    registry = svcs.Registry()

    # this can be used to track what events were received in handlers
    registry.register_value(
        svc_type=fake_handlers.FakeRecorder,
        value=[],
    )
    uow = unit_of_work.FakeUnitOfWork()
    registry.register_value(
        svc_type=unit_of_work.UnitOfWork,
        value=uow,
    )
    bus = messagebus.MessageBus(
        event_handlers=fake_handlers.FAKE_EVENT_HANDLERS,
        command_handlers=fake_handlers.FAKE_COMMAND_HANDLERS,
        registry=registry,
    )
    registry.register_value(
        svc_type=messagebus.MessageBus,
        value=bus,
    )
    sender = email_sender.FakeEmailSender()
    registry.register_value(
        svc_type=BaseEmailSender,
        value=sender,
    )
    return svcs.Container(registry)
