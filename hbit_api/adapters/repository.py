import typing

from sqlalchemy.orm import Session
from sqlmodel import select

from hbit_api.domain import models

T = typing.TypeVar("T")


class SeenTracker(typing.Protocol, typing.Generic[T]):
    def add(self, item: T) -> None: ...

    def get_all(self) -> typing.Collection[T]: ...


class SeenSetTracker(SeenTracker[T]):
    def __init__(self) -> None:
        self._seen: set[T] = set()

    def add(self, item: T) -> None:
        self._seen.add(item)

    def get_all(self) -> set[T]:
        return self._seen


#############
# Protocols #
#############


class EditionRepository(typing.Protocol):
    def add(self, edition: models.Edition) -> None: ...

    def get(self, name: str) -> models.Edition | None: ...

    def get_seen(self) -> typing.Collection[models.Edition]: ...


class UserRepository(typing.Protocol):
    def add(self, user: models.User) -> None: ...

    def get(self, email: str) -> models.User | None: ...

    def get_by_id(self, id: int) -> models.User | None: ...

    def get_seen(self) -> typing.Collection[models.User]: ...

    def delete(self, user: models.User) -> None: ...


class AuthorRepository(typing.Protocol):
    def add(self, user: models.Author) -> None: ...

    def get(self, name: str) -> models.Author | None: ...

    def get_seen(self) -> typing.Collection[models.Author]: ...


###########################
# Concrete Implementation #
###########################


class SqlEditionRepository(EditionRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[models.Edition]
    ) -> None:
        super().__init__()
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, edition: models.Edition) -> None:
        self.session.add(edition)
        self.seen_tracker.add(edition)

    def get(self, name: str) -> models.Edition | None:
        stmt = select(models.Edition).where(models.Edition.name == name)
        edition = self.session.scalar(stmt)
        return edition

    def get_seen(self) -> typing.Collection[models.Edition]:
        return self.seen_tracker.get_all()


class SqlUserRepository(UserRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[models.User]
    ) -> None:
        super().__init__()
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, user: models.User) -> None:
        self.session.add(user)
        self.seen_tracker.add(user)

    def get(self, email: str) -> models.User | None:
        stmt = select(models.User).where(models.User.email == email)
        user = self.session.scalar(stmt)
        return user

    def get_by_id(self, id: int) -> models.User | None:
        stmt = select(models.User).where(models.User.id == id)
        user = self.session.scalar(stmt)
        return user

    def get_seen(self) -> typing.Collection[models.User]:
        return self.seen_tracker.get_all()

    def delete(self, user: models.User) -> None:
        self.session.delete(user)


class SqlAuthorRepository(AuthorRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[models.Author]
    ) -> None:
        super().__init__()
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, user: models.Author) -> None:
        self.session.add(user)
        self.seen_tracker.add(user)

    def get(self, name: str) -> models.Author | None:
        stmt = select(models.Author).where(models.Author.name == name)
        author = self.session.scalar(stmt)
        return author

    def get_seen(self) -> typing.Collection[models.Author]:
        return self.seen_tracker.get_all()
