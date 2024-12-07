import svcs
from sqlalchemy.orm import sessionmaker

from hbit_api.adapters import email_sender
from hbit_api.adapters.orm import start_mappers
from hbit_api.api import deps
from hbit_api.core import db
from hbit_api.service_layer import handlers, messagebus, unit_of_work


def bootstrap(registry: svcs.Registry) -> None:
    start_mappers()
    session_factory = sessionmaker(bind=db.engine)
    registry.register_factory(
        svc_type=deps.SessionFactoryDep,
        factory=session_factory,
    )
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory=session_factory)
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
    sender = email_sender.EmailSender()
    registry.register_value(
        svc_type=email_sender.BaseEmailSender,
        value=sender,
    )
