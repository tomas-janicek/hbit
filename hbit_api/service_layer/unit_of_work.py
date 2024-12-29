import typing

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from hbit_api.adapters import repository
from hbit_api.domain import models

if typing.TYPE_CHECKING:
    from hbit_api.domain import events


class UnitOfWork(typing.Protocol):
    users: repository.UserRepository
    patches: repository.PatchRepository
    cves: repository.CVERepository
    cwes: repository.CWERepository
    capecs: repository.CAPECRepository
    devices: repository.DeviceRepository
    manufacturers: repository.ManufacturerRepository

    def __enter__(self) -> typing.Self: ...

    def __exit__(self, *args: typing.Any) -> None: ...

    def commit(self) -> None: ...

    def collect_new_events(self) -> typing.Iterator["events.Event"]: ...

    def rollback(self) -> None: ...


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

        self.session = self.session_factory()

    def __enter__(self) -> typing.Self:
        self.users = repository.SqlUserRepository(
            session=self.session,
            seen_tracker=repository.SeenSetTracker[models.User](),
        )
        self.patches = repository.SqlPatchRepository(
            session=self.session,
            seen_tracker=repository.SeenSetTracker[models.Patch](),
        )
        self.cves = repository.SqlCVERepository(
            session=self.session,
            seen_tracker=repository.SeenSetTracker[models.CVE](),
        )
        self.cwes = repository.SqlCWERepository(
            session=self.session,
            seen_tracker=repository.SeenSetTracker[models.CWE](),
        )
        self.capecs = repository.SqlCAPECRepository(
            session=self.session,
            seen_tracker=repository.SeenSetTracker[models.CAPEC](),
        )
        self.devices = repository.SqlDeviceRepository(
            session=self.session,
            seen_tracker=repository.SeenSetTracker[models.Device](),
        )
        self.manufacturers = repository.SqlManufacturerRepository(
            session=self.session,
            seen_tracker=repository.SeenSetTracker[models.Manufacturer](),
        )
        return self

    def __exit__(self, *args: typing.Any) -> None:
        self.rollback()
        self.session.close()

    def collect_new_events(self) -> typing.Iterator["events.Event"]:  # noqa: C901
        if hasattr(self, "users"):
            for user in self.users.get_seen():
                while user.events:
                    yield user.events.pop(0)

        if hasattr(self, "patches"):
            for patch in self.patches.get_seen():
                while patch.events:
                    yield patch.events.pop(0)

        if hasattr(self, "cves"):
            for cve in self.cves.get_seen():
                while cve.events:
                    yield cve.events.pop(0)

        if hasattr(self, "cwes"):
            for cwe in self.cwes.get_seen():
                while cwe.events:
                    yield cwe.events.pop(0)

        if hasattr(self, "capecs"):
            for capec in self.capecs.get_seen():
                while capec.events:
                    yield capec.events.pop(0)

        if hasattr(self, "devices"):
            for device in self.devices.get_seen():
                while device.events:
                    yield device.events.pop(0)

        if hasattr(self, "manufacturers"):
            for manufacturer in self.manufacturers.get_seen():
                while manufacturer.events:
                    yield manufacturer.events.pop(0)

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
