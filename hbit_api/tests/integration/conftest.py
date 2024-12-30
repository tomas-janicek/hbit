import typing

import pytest
import svcs
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker
from sqlalchemy.orm.session import Session

from hbit_api.adapters.email_sender import BaseEmailSender
from hbit_api.adapters.orm import metadata, start_mappers
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


@pytest.fixture
def in_memory_sqlite_db() -> Engine:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def sqlite_session_factory(
    in_memory_sqlite_db: Engine,
) -> typing.Iterator[sessionmaker[Session]]:
    start_mappers()
    yield sessionmaker(bind=in_memory_sqlite_db)
    clear_mappers()


@pytest.fixture
def session(sqlite_session_factory: sessionmaker[Session]) -> Session:
    return sqlite_session_factory()
