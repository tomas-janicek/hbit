from typing import Any

import svcs
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from hbit_api import errors
from hbit_api.api import deps
from hbit_api.core.config import settings
from hbit_api.domain import commands
from hbit_api.domain.dto import generic as generic_dto
from hbit_api.domain.dto import users as dto
from hbit_api.views import users as views

router = APIRouter()


@router.get(
    "/",
    response_model=dto.UsersPublic,
)
def read_users(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    skip: int = 0,
    limit: int = 100,
) -> dto.UsersPublic:
    """
    Retrieve users.
    """
    session = services.get(Session)

    return views.read_users(session, skip, limit)


@router.post("/")
def create_user(
    *,
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    create_user: commands.CreateUser,
) -> None:
    bus = services.get(deps.MessageBusDep)
    try:
        bus.handle(create_user)
    except errors.AlreadyExists as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {create_user.email} already exists.",
        ) from error
    return None


@router.patch("/me")
def update_user_me(
    *,
    services: svcs.fastapi.DepContainer,
    current_user: deps.CurrentUser,
    body: dto.UserUpdateDto,
) -> None:
    """
    Update own user.
    """
    bus = services.get(deps.MessageBusDep)
    update_user = commands.UpdateUser(
        id=current_user.id,
        email=body.email,
    )

    try:
        bus.handle(update_user)
    except errors.AlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {update_user.email} already exists.",
        )
    except errors.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User identified by provided data does not exist.",
        )
    return None


@router.patch("/me/password", response_model=generic_dto.Message)
def update_password_me(
    *,
    services: svcs.fastapi.DepContainer,
    current_user: deps.CurrentUser,
    body: dto.UpdatePassword,
) -> generic_dto.Message:
    """
    Update own password.
    """
    bus = services.get(deps.MessageBusDep)
    update_user = commands.UpdateUserPassword(
        id=current_user.id,
        current_password=body.current_password,
        new_password=body.new_password,
    )

    try:
        bus.handle(update_user)
    except errors.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User identified by provided data does not exist.",
        )
    except errors.IncorrectPassword:
        raise HTTPException(status_code=400, detail="Incorrect password")
    except errors.SamePassword:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )

    return generic_dto.Message(message="Password updated successfully")


@router.get("/me", response_model=dto.UserDto)
def read_user_me(current_user: deps.CurrentUser) -> dto.UserDto:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=generic_dto.Message)
def delete_user_me(
    services: svcs.fastapi.DepContainer, current_user: deps.CurrentUser
) -> generic_dto.Message:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )

    bus = services.get(deps.MessageBusDep)
    delete_user = commands.DeleteUser(id=current_user.id)
    bus.handle(delete_user)

    return generic_dto.Message(message="User deleted successfully")


@router.post("/signup", response_model=generic_dto.Message)
def register_user(
    services: svcs.fastapi.DepContainer, create_user: commands.CreateUser
) -> generic_dto.Message:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )

    bus = services.get(deps.MessageBusDep)

    try:
        bus.handle(create_user)
    except errors.AlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {create_user.email} already exists.",
        )

    return generic_dto.Message(message="User successfully created.")


@router.get("/{user_id}", response_model=dto.UserDto)
def read_user_by_id(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    user_id: int,
) -> dto.UserDto:
    """
    Get a specific user by id.
    """
    session = services.get(Session)
    user = views.read_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system.",
        )
    return user


@router.patch("/{user_id}")
def update_user(
    *,
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    user_id: int,
    body: dto.UserUpdateDto,
) -> Any:
    """
    Update a user.
    """
    bus = services.get(deps.MessageBusDep)

    try:
        bus.handle(commands.UpdateUser(id=user_id, email=body.email))
    except errors.DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    except errors.AlreadyExists:
        raise HTTPException(
            status_code=409, detail="User with this email already exists"
        )


@router.delete("/{user_id}")
def delete_user(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    user_id: int,
) -> generic_dto.Message:
    """
    Delete a user.
    """
    if user_id == super_user.id:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )

    bus = services.get(deps.MessageBusDep)
    bus.handle(commands.DeleteUser(id=user_id))

    return generic_dto.Message(message="User deleted successfully")
