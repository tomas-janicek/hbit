import typing

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

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


class UserRepository(typing.Protocol):
    def add(self, user: models.User) -> None: ...

    def get(self, email: str) -> models.User | None: ...

    def get_by_id(self, id: int) -> models.User | None: ...

    def get_seen(self) -> typing.Collection[models.User]: ...

    def delete(self, user: models.User) -> None: ...


class DeviceRepository(typing.Protocol):
    def add(self, device: models.Device) -> None: ...

    def add_or_update(self, device: models.Device) -> models.Device | None: ...

    def get(self, identifier: str) -> models.Device | None: ...

    def get_seen(self) -> typing.Collection[models.Device]: ...


class ManufacturerRepository(typing.Protocol):
    def add(self, manufacturer: models.Manufacturer) -> None: ...

    def get(self, name: str) -> models.Manufacturer | None: ...

    def get_seen(self) -> typing.Collection[models.Manufacturer]: ...


class PatchRepository(typing.Protocol):
    def add(self, patch: models.Patch) -> None: ...

    def add_or_update(self, patch: models.Patch) -> models.Patch | None: ...

    def get(self, build: str) -> models.Patch | None: ...

    def get_seen(self) -> typing.Collection[models.Patch]: ...


class CVERepository(typing.Protocol):
    def add(self, cve: models.CVE) -> None: ...

    def add_or_update(self, cve: models.CVE) -> models.CVE | None: ...

    def get(self, cve_id: str) -> models.CVE | None: ...

    def get_seen(self) -> typing.Collection[models.CVE]: ...


class CWERepository(typing.Protocol):
    def add(self, cwe: models.CWE) -> None: ...

    def add_or_update(self, cwe: models.CWE) -> models.CWE | None: ...

    def get(self, cwe_id: int) -> models.CWE | None: ...

    def get_seen(self) -> typing.Collection[models.CWE]: ...


class CAPECRepository(typing.Protocol):
    def add(self, capec: models.CAPEC) -> None: ...

    def add_or_update(self, capec: models.CAPEC) -> models.CAPEC | None: ...

    def get(self, capec_id: int) -> models.CAPEC | None: ...

    def get_seen(self) -> typing.Collection[models.CAPEC]: ...


###########################
# Concrete Implementation #
###########################


class SqlUserRepository(UserRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[models.User]
    ) -> None:
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, user: models.User) -> None:
        self.session.add(user)
        self.seen_tracker.add(user)

    def get(self, email: str) -> models.User | None:
        stmt = select(models.User).where(models.User.email == email)
        user = self.session.scalar(stmt)

        if user:
            self.seen_tracker.add(user)

        return user

    def get_by_id(self, id: int) -> models.User | None:
        stmt = select(models.User).where(models.User.id == id)
        user = self.session.scalar(stmt)

        if user:
            self.seen_tracker.add(user)

        return user

    def delete(self, user: models.User) -> None:
        self.session.delete(user)
        # TODO: Does this sill work even if I delete user?
        self.seen_tracker.add(user)

    def get_seen(self) -> typing.Collection[models.User]:
        return self.seen_tracker.get_all()


class SqlPatchRepository(PatchRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[models.Patch]
    ) -> None:
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, patch: models.Patch) -> None:
        self.session.add(patch)
        self.seen_tracker.add(patch)

    def add_or_update(self, patch: models.Patch) -> models.Patch | None:
        stmt = insert(models.Patch).values(patch.dict())
        stmt = stmt.on_conflict_do_update(
            index_elements=[models.Patch.build],
            set_={
                "os": stmt.excluded.os,
                "name": stmt.excluded.name,
                "version": stmt.excluded.version,
                "released": stmt.excluded.released,
            },
        ).returning(models.Patch)

        result = self.session.scalar(stmt)
        if result:
            self.seen_tracker.add(result)

        return result

    def get(self, build: str) -> models.Patch | None:
        stmt = select(models.Patch).where(models.Patch.build == build)
        patch = self.session.scalar(stmt)

        if patch:
            self.seen_tracker.add(patch)

        return patch

    def get_seen(self) -> typing.Collection[models.Patch]:
        return self.seen_tracker.get_all()


class SqlDeviceRepository(DeviceRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[models.Device]
    ) -> None:
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, device: models.Device) -> None:
        self.session.add(device)
        self.seen_tracker.add(device)

    def add_or_update(self, device: models.Device) -> models.Device | None:
        stmt = insert(models.Device).values(device.dict())
        stmt = stmt.on_conflict_do_update(
            index_elements=[models.Device.identifier],
            set_={
                "manufacturer_id": device.manufacturer.id,
                "name": stmt.excluded.name,
                "identifier": stmt.excluded.identifier,
                "models": stmt.excluded.models,
                "released": stmt.excluded.released,
                "discontinued": stmt.excluded.discontinued,
                "hardware_info": stmt.excluded.hardware_info,
            },
        ).returning(models.Device)

        result = self.session.scalar(stmt)
        if result:
            self.seen_tracker.add(result)

        return result

    def get(self, identifier: str) -> models.Device | None:
        stmt = select(models.Device).where(models.Device.identifier == identifier)
        device = self.session.scalar(stmt)

        if device:
            self.seen_tracker.add(device)

        return device

    def get_seen(self) -> typing.Collection[models.Device]:
        return self.seen_tracker.get_all()


class SqlManufacturerRepository(ManufacturerRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[models.Manufacturer]
    ) -> None:
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, manufacturer: models.Manufacturer) -> None:
        self.session.add(manufacturer)
        self.seen_tracker.add(manufacturer)

    def get(self, name: str) -> models.Manufacturer | None:
        stmt = select(models.Manufacturer).where(models.Manufacturer.name == name)
        manufacturer = self.session.scalar(stmt)

        if manufacturer:
            self.seen_tracker.add(manufacturer)

        return manufacturer

    def get_seen(self) -> typing.Collection[models.Manufacturer]:
        return self.seen_tracker.get_all()


class SqlCVERepository(CVERepository):
    def __init__(self, session: Session, seen_tracker: SeenTracker[models.CVE]) -> None:
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, cve: models.CVE) -> None:
        self.session.add(cve)
        self.seen_tracker.add(cve)

    def add_or_update(self, cve: models.CVE) -> models.CVE | None:
        stmt = insert(models.CVE).values(cve.dict())
        stmt = stmt.on_conflict_do_update(
            index_elements=[models.CVE.cve_id],
            set_={
                "description": stmt.excluded.description,
                "published": stmt.excluded.published,
                "last_modified": stmt.excluded.last_modified,
                "cvss": stmt.excluded.cvss,
            },
        ).returning(models.CVE)

        result = self.session.scalar(stmt)
        if result:
            self.seen_tracker.add(result)
        return result

    def get(self, cve_id: str) -> models.CVE | None:
        stmt = select(models.CVE).where(models.CVE.cve_id == cve_id)
        cve = self.session.scalar(stmt)

        if cve:
            self.seen_tracker.add(cve)

        return cve

    def get_seen(self) -> typing.Collection[models.CVE]:
        return self.seen_tracker.get_all()


class SqlCWERepository(CWERepository):
    def __init__(self, session: Session, seen_tracker: SeenTracker[models.CWE]) -> None:
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, cwe: models.CWE) -> None:
        self.session.add(cwe)
        self.seen_tracker.add(cwe)

    def add_or_update(self, cwe: models.CWE) -> models.CWE | None:
        stmt = insert(models.CWE).values(cwe.dict())
        stmt = stmt.on_conflict_do_update(
            index_elements=[models.CWE.cwe_id],
            set_={
                "cwe_id": stmt.excluded.cwe_id,
                "name": stmt.excluded.name,
                "description": stmt.excluded.description,
                "extended_description": stmt.excluded.extended_description,
                "likelihood_of_exploit": stmt.excluded.likelihood_of_exploit,
                "background_details": stmt.excluded.background_details,
                "potential_mitigations": stmt.excluded.potential_mitigations,
                "detection_methods": stmt.excluded.detection_methods,
            },
        ).returning(models.CWE)

        result = self.session.scalar(stmt)
        if result:
            self.seen_tracker.add(result)

        return result

    def get(self, cwe_id: int) -> models.CWE | None:
        stmt = select(models.CWE).where(models.CWE.cwe_id == cwe_id)
        cwe = self.session.scalar(stmt)

        if cwe:
            self.seen_tracker.add(cwe)

        return cwe

    def get_seen(self) -> typing.Collection[models.CWE]:
        return self.seen_tracker.get_all()


class SqlCAPECRepository(CAPECRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[models.CAPEC]
    ) -> None:
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, capec: models.CAPEC) -> None:
        self.session.add(capec)
        self.seen_tracker.add(capec)

    def add_or_update(self, capec: models.CAPEC) -> models.CAPEC | None:
        stmt = insert(models.CAPEC).values(capec.dict())
        stmt = stmt.on_conflict_do_update(
            index_elements=[models.CAPEC.capec_id],
            set_={
                "description": stmt.excluded.description,
                "extended_description": stmt.excluded.extended_description,
                "likelihood_of_attack": stmt.excluded.likelihood_of_attack,
                "severity": stmt.excluded.severity,
                "execution_flow": stmt.excluded.execution_flow,
                "prerequisites": stmt.excluded.prerequisites,
                "skills_required": stmt.excluded.skills_required,
                "resources_required": stmt.excluded.resources_required,
                "consequences": stmt.excluded.consequences,
            },
        ).returning(models.CAPEC)
        result = self.session.scalar(stmt)

        if result:
            self.seen_tracker.add(result)

        return result

    def get(self, capec_id: int) -> models.CAPEC | None:
        stmt = select(models.CAPEC).where(models.CAPEC.capec_id == capec_id)
        capec = self.session.scalar(stmt)

        if capec:
            self.seen_tracker.add(capec)

        return capec

    def get_seen(self) -> typing.Collection[models.CAPEC]:
        return self.seen_tracker.get_all()
