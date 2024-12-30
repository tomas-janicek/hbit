import typing

from hbit_api.adapters import repository

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


class SessionObject(typing.Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...


class SessionFactory(typing.Protocol):
    def create_session(self) -> SessionObject: ...
