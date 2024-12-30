import typing

from hbit_api.adapters.repository import SeenSetTracker
from hbit_api.service_layer.unit_of_work import UnitOfWork
from hbit_api.tests.fakes import repository

if typing.TYPE_CHECKING:
    from hbit_api.domain import events


class FakeUnitOfWork(UnitOfWork):
    users: repository.FakeUserRepository
    patches: repository.FakePatchRepository
    cves: repository.FakeCVERepository
    cwes: repository.FakeCWERepository
    capecs: repository.FakeCAPECRepository
    devices: repository.FakeDeviceRepository
    manufacturers: repository.FakeManufacturerRepository

    def __init__(self) -> None:
        self.commited = False

        self.users = repository.FakeUserRepository(  # type: ignore
            data=[],
            seen_tracker=SeenSetTracker(),
        )
        self.patches = repository.FakePatchRepository(  # type: ignore
            data=[],
            seen_tracker=SeenSetTracker(),
        )
        self.cves = repository.FakeCVERepository(  # type: ignore
            data=[],
            seen_tracker=SeenSetTracker(),
        )
        self.cwes = repository.FakeCWERepository(  # type: ignore
            data=[],
            seen_tracker=SeenSetTracker(),
        )
        self.capecs = repository.FakeCAPECRepository(  # type: ignore
            data=[],
            seen_tracker=SeenSetTracker(),
        )
        self.devices = repository.FakeDeviceRepository(  # type: ignore
            data=[],
            seen_tracker=SeenSetTracker(),
        )
        self.manufacturers = repository.FakeManufacturerRepository(  # type: ignore
            data=[],
            seen_tracker=SeenSetTracker(),
        )

    def __enter__(self) -> typing.Self:
        return self

    def __exit__(self, *args: typing.Any) -> None:
        self.rollback()

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
        self.commited = True

    def rollback(self) -> None:
        pass
