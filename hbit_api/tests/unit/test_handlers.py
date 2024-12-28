import svcs
from pydantic import SecretStr

from hbit_api.adapters import email_sender
from hbit_api.domain import commands
from hbit_api.service_layer import messagebus, unit_of_work
from hbit_api.tests.fakes.email_sender import FakeEmailSender
from hbit_api.tests.fakes.unit_of_work import FakeUnitOfWork


def test_add_user(services: svcs.Container) -> None:
    bus = services.get(messagebus.MessageBus)
    uow: FakeUnitOfWork = services.get(unit_of_work.UnitOfWork)  # type: ignore
    sender: FakeEmailSender = services.get(email_sender.BaseEmailSender)  # type: ignore

    create_user = commands.CreateUser(
        email="example@email.com",
        name="Example",
        password=SecretStr("valid_Password123"),
    )
    bus.handle(create_user)

    # test user was created
    assert len(uow.users.data) == 1
    user = uow.users.data[0]
    assert user
    assert user.email == create_user.email
    assert user.hashed_password != create_user.password.get_secret_value()
    # test verification email was send to user
    assert len(sender.send_emails) == 1
    send_email = sender.send_emails[0]
    assert send_email.email_to == create_user.email
    assert send_email.subject
