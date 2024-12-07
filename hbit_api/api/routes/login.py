from typing import Annotated

import svcs
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from hbit_api import errors
from hbit_api.api import deps
from hbit_api.api.deps import CurrentUser
from hbit_api.domain import commands
from hbit_api.domain.dto import generic as generic_dto
from hbit_api.domain.dto import users as dto

router = APIRouter()


@router.post("/login/access-token")
def login_access_token(
    services: svcs.fastapi.DepContainer,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dto.Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    bus = services.get(deps.MessageBusDep)
    authenticate = commands.LogInUser(
        email=form_data.username, password=form_data.password
    )

    try:
        token = bus.handle(authenticate)
    except errors.DoesNotExist:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    except errors.InActiveUser:
        raise HTTPException(status_code=400, detail="Inactive user")

    return token


@router.post("/login/test-token", response_model=dto.UserDto)
def test_token(current_user: CurrentUser) -> dto.UserDto:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(
    services: svcs.fastapi.DepContainer, email: EmailStr
) -> generic_dto.Message:
    """
    Password Recovery
    """
    bus = services.get(deps.MessageBusDep)
    recover_user_password = commands.RecoverUserPassword(email=email)

    try:
        bus.handle(recover_user_password)
    except errors.DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )

    return generic_dto.Message(message="Password recovery email sent")


@router.post("/reset-password/")
def reset_password(
    services: svcs.fastapi.DepContainer, reset_password: commands.ResetPassword
) -> generic_dto.Message:
    """
    Reset password
    """

    bus = services.get(deps.MessageBusDep)

    try:
        bus.handle(reset_password)
    except errors.DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    except errors.InActiveUser:
        raise HTTPException(status_code=400, detail="Inactive user")

    return generic_dto.Message(message="Password updated successfully")
