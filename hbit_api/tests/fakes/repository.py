import typing

from hbit_api.adapters import repository
from hbit_api.domain import models

T = typing.TypeVar("T")


def _get_from(data: typing.Collection[T], field: str, key: typing.Any) -> T | None:
    for d in data:
        if getattr(d, field) == key:
            return d
    return None


class FakeUserRepository(repository.UserRepository):
    def __init__(
        self, data: list[models.User], seen_tracker: repository.SeenTracker[models.User]
    ) -> None:
        self.data = data
        self.seen_tracker = seen_tracker

    def add(self, user: models.User) -> None:
        self.data.append(user)
        # set if to object index in data list
        user.id = self.data.index(user)
        self.seen_tracker.add(user)

    def get(self, email: str) -> models.User | None:
        user = _get_from(self.data, field="email", key=email)
        if user:
            self.seen_tracker.add(user)
        return user

    def get_by_id(self, id: int) -> models.User | None:
        user = _get_from(self.data, field="id", key=id)
        if user:
            self.seen_tracker.add(user)
        return user

    def delete(self, user: models.User) -> None:
        self.data.remove(user)
        self.seen_tracker.add(user)

    def get_seen(self) -> typing.Collection[models.User]:
        return self.seen_tracker.get_all()


class FakePatchRepository(repository.PatchRepository):
    def __init__(
        self,
        data: list[models.Patch],
        seen_tracker: repository.SeenTracker[models.Patch],
    ) -> None:
        self.data = data
        self.seen_tracker = seen_tracker

    def add(self, patch: models.Patch) -> None:
        self.data.append(patch)
        self.seen_tracker.add(patch)

    def add_or_update(self, patch: models.Patch) -> models.Patch | None:
        if self.get(patch.build):
            self.data.remove(patch)
            self.data.append(patch)
        else:
            self.data.append(patch)

        self.seen_tracker.add(patch)

        return patch

    def get(self, build: str) -> models.Patch | None:
        patch = _get_from(self.data, field="build", key=build)
        if patch:
            self.seen_tracker.add(patch)
        return patch

    def get_seen(self) -> typing.Collection[models.Patch]:
        return self.seen_tracker.get_all()


class FakeDeviceRepository(repository.DeviceRepository):
    def __init__(
        self,
        data: list[models.Device],
        seen_tracker: repository.SeenTracker[models.Device],
    ) -> None:
        self.data = data
        self.seen_tracker = seen_tracker

    def add(self, device: models.Device) -> None:
        self.data.append(device)
        self.seen_tracker.add(device)

    def add_or_update(self, device: models.Device) -> models.Device | None:
        if self.get(device.identifier):
            self.data.remove(device)
            self.data.append(device)
        else:
            self.data.append(device)

        self.seen_tracker.add(device)

        return device

    def get(self, identifier: str) -> models.Device | None:
        device = _get_from(self.data, field="identifier", key=identifier)
        if device:
            self.seen_tracker.add(device)
        return device

    def get_seen(self) -> typing.Collection[models.Device]:
        return self.seen_tracker.get_all()


class FakeManufacturerRepository(repository.ManufacturerRepository):
    def __init__(
        self,
        data: list[models.Manufacturer],
        seen_tracker: repository.SeenTracker[models.Manufacturer],
    ) -> None:
        self.data = data
        self.seen_tracker = seen_tracker

    def add(self, manufacturer: models.Manufacturer) -> None:
        self.data.append(manufacturer)
        self.seen_tracker.add(manufacturer)

    def get(self, name: str) -> models.Manufacturer | None:
        manufacturer = _get_from(self.data, field="name", key=name)
        if manufacturer:
            self.seen_tracker.add(manufacturer)
        return manufacturer

    def get_seen(self) -> typing.Collection[models.Manufacturer]:
        return self.seen_tracker.get_all()


class FakeCVERepository(repository.CVERepository):
    def __init__(
        self, data: list[models.CVE], seen_tracker: repository.SeenTracker[models.CVE]
    ) -> None:
        self.data = data
        self.seen_tracker = seen_tracker

    def add(self, cve: models.CVE) -> None:
        self.data.append(cve)
        self.seen_tracker.add(cve)

    def add_or_update(self, cve: models.CVE) -> models.CVE | None:
        if self.get(cve.cve_id):
            self.data.remove(cve)
            self.data.append(cve)
        else:
            self.data.append(cve)

        self.seen_tracker.add(cve)

        return cve

    def get(self, cve_id: str) -> models.CVE | None:
        cve = _get_from(self.data, field="cve_id", key=cve_id)
        if cve:
            self.seen_tracker.add(cve)
        return cve

    def get_seen(self) -> typing.Collection[models.CVE]:
        return self.seen_tracker.get_all()


class FakeCWERepository(repository.CWERepository):
    def __init__(
        self, data: list[models.CWE], seen_tracker: repository.SeenTracker[models.CWE]
    ) -> None:
        self.data = data
        self.seen_tracker = seen_tracker

    def add(self, cwe: models.CWE) -> None:
        self.data.append(cwe)
        self.seen_tracker.add(cwe)

    def add_or_update(self, cwe: models.CWE) -> models.CWE | None:
        if self.get(cwe.cwe_id):
            self.data.remove(cwe)
            self.data.append(cwe)
        else:
            self.data.append(cwe)

        self.seen_tracker.add(cwe)

        return cwe

    def get(self, cwe_id: int) -> models.CWE | None:
        cwe = _get_from(self.data, field="cwe_id", key=cwe_id)
        if cwe:
            self.seen_tracker.add(cwe)
        return cwe

    def get_seen(self) -> typing.Collection[models.CWE]:
        return self.seen_tracker.get_all()


class FakeCAPECRepository(repository.CAPECRepository):
    def __init__(
        self,
        data: list[models.CAPEC],
        seen_tracker: repository.SeenTracker[models.CAPEC],
    ) -> None:
        self.data = data
        self.seen_tracker = seen_tracker

    def add(self, capec: models.CAPEC) -> None:
        self.data.append(capec)
        self.seen_tracker.add(capec)

    def add_or_update(self, capec: models.CAPEC) -> models.CAPEC | None:
        if self.get(capec.capec_id):
            self.data.remove(capec)
            self.data.append(capec)
        else:
            self.data.append(capec)

        self.seen_tracker.add(capec)

        return capec

    def get(self, capec_id: int) -> models.CAPEC | None:
        capec = _get_from(self.data, field="capec_id", key=capec_id)
        if capec:
            self.seen_tracker.add(capec)
        return capec

    def get_seen(self) -> typing.Collection[models.CAPEC]:
        return self.seen_tracker.get_all()
