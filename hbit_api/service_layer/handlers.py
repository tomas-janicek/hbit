from datetime import timedelta

import jose
import svcs
from jose import jwt
from pydantic import ValidationError

from hbit_api import errors, utils
from hbit_api.core import security
from hbit_api.core.config import settings
from hbit_api.domain import commands, events, models
from hbit_api.domain.dto import users as dto

from . import unit_of_work


def login_user(
    cmd: commands.LogInUser,
    services: svcs.Container,
) -> dto.Token:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        user = uow.users.get(email=cmd.email)
        if not user:
            raise errors.DoesNotExist()
        elif not security.verify_password(cmd.password, user.hashed_password):
            raise errors.DoesNotExist()
        elif not user.is_active:
            raise errors.InActiveUser()

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return dto.Token(
            access_token=security.create_access_token(
                user.id, expires_delta=access_token_expires
            )
        )


def authenticate_user(
    cmd: commands.AuthenticateUser,
    services: svcs.Container,
) -> dto.UserDto:
    uow = services.get(unit_of_work.UnitOfWork)
    try:
        payload = jwt.decode(
            cmd.token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = dto.TokenPayload(**payload)
    except (jose.JWTError, ValidationError) as error:
        raise errors.InvalidToken() from error
    with uow:
        user = uow.users.get_by_id(id=int(token_data.sub))

        if not user:
            raise errors.DoesNotExist()
        if not user.is_active:
            raise errors.InActiveUser()
        return dto.UserDto(
            id=user.id,  # type: ignore
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )


def add_author(
    cmd: commands.CreateAuthor,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        author = models.Author(name=cmd.name, books=[])
        uow.authors.add(author)
        uow.commit()


def add_book(
    cmd: commands.CreateBook,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        edition = uow.editions.get(name=cmd.name)
        if edition is None:
            edition = models.Edition(name=cmd.name, books=[])
            uow.editions.add(edition)
        edition.books.append(models.Book(name=cmd.name, authors=[]))
        uow.commit()


def add_user(
    cmd: commands.CreateUser,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        user = uow.users.get(cmd.email)
        if user:
            raise errors.AlreadyExists()

        user = models.User(
            email=cmd.email,
            name=cmd.name,
            hashed_password=security.get_password_hash(cmd.password.get_secret_value()),
            is_superuser=cmd.is_superuser,
        )
        uow.users.add(user)
        user.send_verification_email()

        uow.commit()


def update_user(
    cmd: commands.UpdateUser,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        user = uow.users.get_by_id(cmd.id)
        if not user:
            raise errors.DoesNotExist()
        if cmd.name:
            user.name = cmd.name
        if cmd.email:
            existing_user = uow.users.get(email=cmd.email)
            if existing_user and existing_user.id != user.id:
                raise errors.AlreadyExists()
            user.email = cmd.email

        uow.commit()


def update_user_password(
    cmd: commands.UpdateUserPassword,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        user = uow.users.get_by_id(cmd.id)

        if not user:
            raise errors.DoesNotExist()
        if not security.verify_password(
            cmd.current_password.get_secret_value(), user.hashed_password
        ):
            raise errors.IncorrectPassword()
        if cmd.current_password == cmd.new_password:
            raise errors.SamePassword()
        hashed_password = security.get_password_hash(
            cmd.new_password.get_secret_value()
        )
        user.hashed_password = hashed_password

        uow.commit()


def recover_user_password(
    cmd: commands.RecoverUserPassword,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        user = uow.users.get(cmd.email)

        if not user:
            raise errors.DoesNotExist()

        user.send_password_recovery_email()
        uow.commit()


def reset_password(
    cmd: commands.ResetPassword,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    email = utils.verify_password_reset_token(token=cmd.token)

    if not email:
        raise errors.InvalidToken()

    with uow:
        user = uow.users.get(email=email)
        if not user:
            raise errors.DoesNotExist()
        elif not user.is_active:
            raise errors.InActiveUser()

        hashed_password = security.get_password_hash(password=cmd.new_password)
        user.hashed_password = hashed_password

        uow.commit()


def delete_user(
    cmd: commands.DeleteUser,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        user = uow.users.get_by_id(id=cmd.id)
        if not user:
            raise errors.DoesNotExist()
        uow.users.delete(user)

        uow.commit()


def send_new_account_email(
    event: events.NotifyNewAccount,
    services: svcs.Container,
) -> None:
    if settings.emails_enabled:
        email_data = utils.generate_new_account_email(
            email_to=event.email, username=event.email
        )
        # TODO: Create email sender service so we can fake this
        utils.send_email(
            email_to=event.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )


def send_password_recovery_email(
    event: events.NotifyRecoverPassword,
    services: svcs.Container,
) -> None:
    password_reset_token = utils.generate_password_reset_token(email=event.email)
    email_data = utils.generate_reset_password_email(
        email_to=event.email, email=event.email, token=password_reset_token
    )
    # TODO: Create email sender service so we can fake this
    utils.send_email(
        email_to=event.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )


EVENT_HANDLERS: events.EventHandlersConfig = {
    events.NotifyNewAccount: (send_new_account_email,),
    events.NotifyRecoverPassword: (send_password_recovery_email,),
}

COMMAND_HANDLERS: commands.CommandHandlerConfig = {
    commands.LogInUser: login_user,
    commands.AuthenticateUser: authenticate_user,
    commands.CreateAuthor: add_author,
    commands.CreateBook: add_book,
    commands.CreateUser: add_user,
    commands.UpdateUser: update_user,
    commands.UpdateUserPassword: update_user_password,
    commands.DeleteUser: delete_user,
}
