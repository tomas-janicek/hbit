import pytest
import svcs
from pydantic import SecretStr

from hbit_api import errors
from hbit_api.adapters import email_sender
from hbit_api.domain import commands
from hbit_api.domain.dto import users as users_dto
from hbit_api.service_layer import messagebus, unit_of_work
from hbit_api.tests.fakes.email_sender import FakeEmailSender
from hbit_api.tests.fakes.unit_of_work import FakeUnitOfWork


def test_login_user(services: svcs.Container) -> None:
    bus = services.get(messagebus.MessageBus)

    # arrange
    create_user = commands.CreateUser(
        email="example@email.com",
        name="Example",
        password=SecretStr("valid_Password123"),
    )
    bus.handle(create_user)

    # act
    log_in_user = commands.LogInUser(
        email=create_user.email, password=create_user.password
    )
    token = bus.handle(log_in_user)

    # assert
    assert token
    assert token.token_type == "bearer"
    assert token.access_token


def test_login_bad_password(services: svcs.Container) -> None:
    bus = services.get(messagebus.MessageBus)

    # arrange
    create_user = commands.CreateUser(
        email="example@email.com",
        name="Example",
        password=SecretStr("valid_Password123"),
    )
    bus.handle(create_user)

    # act & assert raises
    log_in_user = commands.LogInUser(
        email=create_user.email, password=SecretStr("bad-password")
    )
    with pytest.raises(errors.IncorrectPassword):
        _token = bus.handle(log_in_user)


def test_login_bad_email(services: svcs.Container) -> None:
    bus = services.get(messagebus.MessageBus)

    # arrange
    create_user = commands.CreateUser(
        email="example@email.com",
        name="Example",
        password=SecretStr("valid_Password123"),
    )
    bus.handle(create_user)

    # act & assert raises
    log_in_user = commands.LogInUser(
        email="bad@email.com", password=create_user.password
    )
    with pytest.raises(errors.DoesNotExist):
        _token = bus.handle(log_in_user)


def test_authenticate(services: svcs.Container) -> None:
    bus = services.get(messagebus.MessageBus)

    # arrange
    # create user
    create_user = commands.CreateUser(
        email="example@email.com",
        name="Example",
        password=SecretStr("valid_Password123"),
    )
    bus.handle(create_user)
    # get token by logging in created user
    log_in_user = commands.LogInUser(
        email=create_user.email, password=create_user.password
    )
    token = bus.handle(log_in_user)

    # act
    authenticate_user = commands.AuthenticateUser(token=token.access_token)
    user_dto: users_dto.UserDto = bus.handle(authenticate_user)

    # assert
    assert user_dto
    assert user_dto.email == create_user.email


def test_authenticate_bad_token(services: svcs.Container) -> None:
    bus = services.get(messagebus.MessageBus)

    # arrange
    # create user
    create_user = commands.CreateUser(
        email="example@email.com",
        name="Example",
        password=SecretStr("valid_Password123"),
    )
    bus.handle(create_user)

    # act & assert raises
    authenticate_user = commands.AuthenticateUser(token="bad-token")
    with pytest.raises(errors.InvalidToken):
        bus.handle(authenticate_user)


def test_add_user(services: svcs.Container) -> None:
    bus = services.get(messagebus.MessageBus)
    uow: FakeUnitOfWork = services.get(unit_of_work.UnitOfWork)  # type: ignore
    sender: FakeEmailSender = services.get(email_sender.BaseEmailSender)  # type: ignore

    # act
    create_user = commands.CreateUser(
        email="example@email.com",
        name="Example",
        password=SecretStr("valid_Password123"),
    )
    bus.handle(create_user)

    # assert
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
