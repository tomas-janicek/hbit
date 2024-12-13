from sqlalchemy.orm import Session
from sqlmodel import func, select

from hbit_api.domain import models
from hbit_api.domain.dto import users as dto


def read_users(session: Session, skip: int = 0, limit: int = 100) -> dto.Users:
    count_statement = select(func.count()).select_from(models.User)
    # count statement always return 0 even if there are no users
    count = session.scalar(count_statement)

    statement = select(models.User).offset(skip).limit(limit)
    users = session.scalars(statement).all()

    users_dtos = [dto.UserDto.from_user(u) for u in users]
    return dto.Users(data=users_dtos, count=count)  # type: ignore


def read_user_by_id(session: Session, id: int) -> dto.UserDto | None:
    stmt = select(models.User).where(models.User.id == id)
    user = session.scalar(stmt)

    return dto.UserDto.from_user(user) if user else None
