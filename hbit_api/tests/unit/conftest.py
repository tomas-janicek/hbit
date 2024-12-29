import pytest
import svcs

from hbit_api.adapters.email_sender import BaseEmailSender
from hbit_api.service_layer import handlers, messagebus
from hbit_api.tests.fakes import email_sender, unit_of_work


@pytest.fixture
def services() -> svcs.Container:
    registry = svcs.Registry()

    uow = unit_of_work.FakeUnitOfWork()
    registry.register_value(
        svc_type=unit_of_work.UnitOfWork,
        value=uow,
    )
    bus = messagebus.MessageBus(
        event_handlers=handlers.EVENT_HANDLERS,
        command_handlers=handlers.COMMAND_HANDLERS,
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
