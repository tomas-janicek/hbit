import logging
from datetime import timedelta

import jose
import svcs
from jose import jwt
from pydantic import ValidationError

from hbit_api import errors, utils
from hbit_api.adapters import email_sender
from hbit_api.core import security
from hbit_api.core.config import settings
from hbit_api.domain import commands, events, models
from hbit_api.domain.dto import users as dto

from . import unit_of_work

_log = logging.getLogger(__name__)


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


def add_cwes(
    cmd: commands.CreateCWEs,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        cwes = [cwe.model_dump() for cwe in cmd.cwe_batch]
        uow.cwes.add_or_update(cwes)

        uow.commit()


def add_capecs(
    cmd: commands.CreateCAPECs,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        for capec_in in cmd.capec_batch:
            uow.capecs.add_or_update(capec_in.model_dump(exclude={"cwe_ids"}))
            capec = uow.capecs.get(capec_in.capec_id)
            if not capec:
                raise errors.DoesNotExist(
                    f"CAPEC with ID {capec_in.capec_id} could not be created."
                )

            for cwe_id in capec_in.cwe_ids:
                cwe = uow.cwes.get(cwe_id)
                if not cwe:
                    _log.warning(
                        "Error mapping CAPEC with ID %s to CWE with ID %s. "
                        "CWE with this ID does not exists.",
                        capec.capec_id,
                        cwe_id,
                    )
                    continue

                cwe.capecs.append(capec)

        uow.commit()


def add_patch(
    cmd: commands.CreatePatches,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        patches = [patch.model_dump() for patch in cmd.patches_batch]
        uow.patches.add_or_update(patches)

        uow.commit()


def add_cves(
    cmd: commands.CreateCVEs,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        patch = uow.patches.get(cmd.patch_build)
        if not patch:
            raise errors.DoesNotExist(
                f"Error mapping CVEs to Patch with build {cmd.patch_build}. "
                "Patch with this build does not exist.",
            )

        for cve_in in cmd.cve_batch:
            uow.cves.add_or_update(cve_in.model_dump(exclude={"cwe_ids"}))
            cve = uow.cves.get(cve_in.cve_id)
            if not cve:
                raise errors.DoesNotExist()

            for cwe_id in cve_in.cwe_ids:
                cwe = uow.cwes.get(cwe_id)
                if not cwe:
                    _log.warning(
                        "Error mapping CVE with ID %s to CWE with ID %s. "
                        "CWE with this ID does not exists.",
                        cve.cve_id,
                        cwe_id,
                    )
                    continue

                cve.cwes.append(cwe)

            patch.cves.append(cve)

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
    sender = services.get(email_sender.BaseEmailSender)

    if settings.emails_enabled:
        email_data = utils.generate_new_account_email(
            email_to=event.email, username=event.email
        )
        sender.send_email(
            email_to=event.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )


def send_password_recovery_email(
    event: events.NotifyRecoverPassword,
    services: svcs.Container,
) -> None:
    sender = services.get(email_sender.BaseEmailSender)

    password_reset_token = utils.generate_password_reset_token(email=event.email)
    email_data = utils.generate_reset_password_email(
        email_to=event.email, email=event.email, token=password_reset_token
    )
    sender.send_email(
        email_to=event.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )


def send_test_email(
    event: events.TestNotify,
    services: svcs.Container,
) -> None:
    sender = services.get(email_sender.BaseEmailSender)

    email_data = utils.generate_test_email(email_to=event.email)
    sender.send_email(
        email_to=event.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )


EVENT_HANDLERS: events.EventHandlersConfig = {
    events.NotifyNewAccount: (send_new_account_email,),
    events.NotifyRecoverPassword: (send_password_recovery_email,),
    events.TestNotify: (send_test_email,),
}

COMMAND_HANDLERS: commands.CommandHandlerConfig = {
    commands.LogInUser: login_user,
    commands.AuthenticateUser: authenticate_user,
    commands.CreateUser: add_user,
    commands.CreateCWEs: add_cwes,
    commands.CreateCAPECs: add_capecs,
    commands.CreateCVEs: add_cves,
    commands.CreatePatches: add_patch,
    commands.UpdateUser: update_user,
    commands.UpdateUserPassword: update_user_password,
    commands.DeleteUser: delete_user,
}
