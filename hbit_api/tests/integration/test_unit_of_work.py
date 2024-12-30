import pytest
from sqlalchemy import func
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import select

from hbit_api.domain import models
from hbit_api.service_layer import unit_of_work
from hbit_api.tests.fakes import handlers


def test_enter(session_factory: sessionmaker[Session]) -> None:
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow:
        # just random three repositories
        assert uow.users
        assert uow.manufacturers
        assert uow.cves


def test_commit(session_factory: sessionmaker[Session]) -> None:
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow:
        user = models.User(
            email="test@email.com",
            name="test",
            hashed_password="hashed-password",
            is_active=True,
            is_superuser=False,
        )
        uow.users.add(user)

        uow.commit()

        stmt = select(models.User).where(models.User.email == user.email)
        created_user = uow.session.scalar(stmt)

        assert created_user
        assert created_user == user


def test_rollback(session_factory: sessionmaker[Session]) -> None:
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow:
        user = models.User(
            email="test@email.com",
            name="test",
            hashed_password="hashed-password",
            is_active=True,
            is_superuser=False,
        )
        uow.users.add(user)

        uow.rollback()

        stmt = select(func.count()).select_from(models.User)
        count = uow.session.scalar(stmt)

        assert count == 0


def test_rollback_if_not_commited(session_factory: sessionmaker[Session]) -> None:
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow:
        user = models.User(
            email="test@email.com",
            name="test",
            hashed_password="hashed-password",
            is_active=True,
            is_superuser=False,
        )
        uow.users.add(user)

    with uow:
        stmt = select(func.count()).select_from(models.User)
        count = uow.session.scalar(stmt)

        assert count == 0


def test_exit(session_factory: sessionmaker[Session]) -> None:
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory=session_factory)
    with pytest.raises(ValueError):
        with uow:
            user = models.User(
                email="test@email.com",
                name="test",
                hashed_password="hashed-password",
                is_active=True,
                is_superuser=False,
            )
            uow.users.add(user)

            raise ValueError()

    with uow:
        stmt = select(func.count()).select_from(models.User)
        count = uow.session.scalar(stmt)

        assert count == 0


def test_collect_events(session_factory: sessionmaker[Session]) -> None:
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory=session_factory)
    fake_event = handlers.FakeEvent(message="fake-event")

    with uow:
        user = models.User(
            email="test@email.com",
            name="test",
            hashed_password="hashed-password",
            is_active=True,
            is_superuser=False,
        )
        uow.users.add(user)

        user.events.append(fake_event)

        uow.commit()

    events = list(uow.collect_new_events())
    assert len(events) == 1
    assert events[0] == fake_event
