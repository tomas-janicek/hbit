from dataclasses import dataclass, field

from hbit_api.domain import events


@dataclass
class User:
    email: str
    full_name: str | None
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    id: int | None = None

    events: list["events.Event"] = field(default_factory=list)

    def send_verification_email(self) -> None:
        send_new_account_email = events.NotifyNewAccount(email=self.email)
        self.events.append(send_new_account_email)

    def send_password_recovery_email(self) -> None:
        send_new_account_email = events.NotifyRecoverPassword(email=self.email)
        self.events.append(send_new_account_email)

    def __hash__(self) -> int:
        # TODO: normalize
        return hash(self.email)


@dataclass
class Author:
    name: str
    books: list["Book"]
    id: int | None = None

    events: list["events.Event"] = field(default_factory=list)

    def __hash__(self) -> int:
        # TODO: normalize
        return hash(self.name.lower())


@dataclass
class Book:
    name: str
    authors: list["Author"]
    id: int | None = None

    def __hash__(self) -> int:
        # TODO: normalize
        return hash(self.name.lower())


@dataclass
class Edition:
    name: str
    books: list["Book"]
    events: list["events.Event"] = field(default_factory=list)
    id: int | None = None

    def __hash__(self) -> int:
        # TODO: normalize
        return hash(self.name.lower())
