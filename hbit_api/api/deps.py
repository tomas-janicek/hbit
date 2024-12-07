import typing
from typing import Annotated

import svcs
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, sessionmaker

from hbit_api import errors
from hbit_api.core import db
from hbit_api.core.config import settings
from hbit_api.domain import commands, model
from hbit_api.domain.dto import users as dto
from hbit_api.service_layer import messagebus, unit_of_work

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> typing.Iterator[Session]:
    with Session(db.engine) as session:
        yield session


def get_current_user_id(
    services: svcs.fastapi.DepContainer, token: "TokenDep"
) -> dto.UserDto:
    bus = services.get(MessageBusDep)
    authenticate_user = commands.AuthenticateUser(token=token)

    try:
        user: dto.UserDto = bus.handle(authenticate_user)
    except errors.DoesNotExist as error:
        raise HTTPException(status_code=404, detail="User not found") from error
    except errors.InActiveUser as error:
        raise HTTPException(status_code=400, detail="Inactive user") from error
    except errors.InvalidToken as error:
        raise HTTPException(status_code=400, detail="Invalid token") from error

    return user


def get_current_active_superuser(current_user: "CurrentUser") -> dto.UserDto:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


# TODO: Get rid of this. Get session form registry or use UoW!
SessionFactoryDep = sessionmaker[Session]
UoWDep = unit_of_work.UnitOfWork
MessageBusDep = messagebus.MessageBus
# TODO: Get rid of this. Get session form registry or use UoW!
SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

CurrentUser = Annotated[dto.UserDto, Depends(get_current_user_id)]
CurrentSuperUser = Annotated[model.User, Depends(get_current_active_superuser)]
