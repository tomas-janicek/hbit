from typing import Annotated

import svcs
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from hbit_api import errors
from hbit_api.core.config import settings
from hbit_api.domain import commands, models
from hbit_api.domain.dto import users as dto
from hbit_api.service_layer import messagebus

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_current_user(
    services: svcs.fastapi.DepContainer, token: "TokenDep"
) -> dto.UserDto:
    bus = services.get(messagebus.MessageBus)
    authenticate_user = commands.AuthenticateUser(token=token)

    try:
        user: dto.UserDto = bus.handle(authenticate_user)
    except errors.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except errors.InActiveUser:
        raise HTTPException(status_code=400, detail="Inactive user")
    except errors.InvalidToken:
        raise HTTPException(status_code=400, detail="Invalid token")

    return user


def get_current_active_superuser(current_user: "CurrentUser") -> dto.UserDto:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


SessionFactoryDep = Session

TokenDep = Annotated[str, Depends(reusable_oauth2)]
CurrentUser = Annotated[dto.UserDto, Depends(get_current_user)]
CurrentSuperUser = Annotated[models.User, Depends(get_current_active_superuser)]
