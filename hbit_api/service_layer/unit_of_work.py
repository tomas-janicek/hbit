import typing

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from hbit_api.adapters import repository
from hbit_api.domain import models

if typing.TYPE_CHECKING:
    from hbit_api.domain import events


class UnitOfWork(typing.Protocol):
    editions: repository.EditionRepository
    users: repository.UserRepository
    authors: repository.AuthorRepository

    def __enter__(self) -> typing.Self: ...

    def __exit__(self, *args: typing.Any) -> None: ...

    def commit(self) -> None: ...

    def collect_new_events(self) -> typing.Iterator["events.Event"]: ...

    def rollback(self) -> None: ...


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.users = repository.SqlUserRepository(
            session=self.session,
            seen_tracker=repository.SeenSetTracker[models.User](),
        )
        self.editions = repository.SqlEditionRepository(
            session=self.session,
            seen_tracker=repository.SeenSetTracker[models.Edition](),
        )
        self.authors = repository.SqlAuthorRepository(
            session=self.session,
            seen_tracker=repository.SeenSetTracker[models.Author](),
        )
        return self

    def __exit__(self, *args: typing.Any) -> None:
        self.rollback()
        self.session.close()

    def collect_new_events(self) -> typing.Iterator["events.Event"]:
        for bibliography in self.editions.get_seen():
            while bibliography.events:
                yield bibliography.events.pop(0)

        for user in self.users.get_seen():
            while user.events:
                yield user.events.pop(0)

        for author in self.authors.get_seen():
            while author.events:
                yield author.events.pop(0)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
