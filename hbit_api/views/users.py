from sqlalchemy.orm import Session
from sqlmodel import func, select

from hbit_api.domain import model
from hbit_api.domain.dto import users as dto


def read_users(session: Session, skip: int = 0, limit: int = 100) -> dto.UsersPublic:
    count_statement = select(func.count()).select_from(model.User)
    # TODO: Should I use or 0 here?
    count = session.scalar(count_statement)

    statement = select(model.User).offset(skip).limit(limit)
    users = session.scalars(statement).all()

    users_dtos = [dto.UserDto.from_user(u) for u in users]
    return dto.UsersPublic(data=users_dtos, count=count)  # type: ignore


def read_user_by_id(session: Session, id: int) -> dto.UserDto | None:
    stmt = select(model.User).where(model.User.id == id)
    user = session.scalar(stmt)

    return dto.UserDto.from_user(user) if user else None
