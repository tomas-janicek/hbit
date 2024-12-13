import typing

from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session
from sqlmodel import select

from hbit_api.domain import models

T = typing.TypeVar("T")
PreparedValues = (
    typing.Sequence[typing.Mapping[str, typing.Any]] | typing.Mapping[str, typing.Any]
)


# TODO: Where should I use seen tracker?
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

    def add_or_update(self, device_dicts: PreparedValues) -> None: ...

    def get(self, identifier: str) -> models.Device | None: ...

    def get_seen(self) -> typing.Collection[models.Device]: ...


class ManufacturerRepository(typing.Protocol):
    def add(self, manufacturer: models.Manufacturer) -> None: ...

    def get(self, name: str) -> models.Manufacturer | None: ...

    def get_seen(self) -> typing.Collection[models.Manufacturer]: ...


class PatchRepository(typing.Protocol):
    def add(self, patch: models.Patch) -> None: ...

    def add_or_update(self, patch_dicts: PreparedValues) -> None: ...

    def get(self, build: str) -> models.Patch | None: ...

    def get_seen(self) -> typing.Collection[models.Patch]: ...


class CVERepository(typing.Protocol):
    def add(self, patch: models.CVE) -> None: ...

    def add_or_update(self, cve_dicts: PreparedValues) -> None: ...

    def get(self, cve_id: str) -> models.CVE | None: ...

    def get_seen(self) -> typing.Collection[models.CVE]: ...


class CWERepository(typing.Protocol):
    def add(self, cwe: models.CWE) -> None: ...

    def add_or_update(self, cwe_dicts: PreparedValues) -> None: ...

    def get(self, cwe_id: int) -> models.CWE | None: ...

    def get_seen(self) -> typing.Collection[models.CWE]: ...


class CAPECRepository(typing.Protocol):
    def add(self, capec: models.CAPEC) -> None: ...

    def add_or_update(self, capec_dicts: PreparedValues) -> None: ...

    def get(self, capec_id: int) -> models.CAPEC | None: ...

    def get_seen(self) -> typing.Collection[models.CAPEC]: ...


###########################
# Concrete Implementation #
###########################


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


class SqlPatchRepository(PatchRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[models.Patch]
    ) -> None:
        super().__init__()
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, patch: models.Patch) -> None:
        self.session.add(patch)
        self.seen_tracker.add(patch)

    def add_or_update(self, patch_dicts: PreparedValues) -> None:
        stmt = insert(models.Patch).values(patch_dicts)
        stmt = stmt.on_conflict_do_update(
            index_elements=[models.Patch.build],
            set_={
                "os": stmt.excluded.os,
                "name": stmt.excluded.name,
                "version": stmt.excluded.version,
                "released": stmt.excluded.released,
            },
        )
        self.session.execute(stmt)

    def get(self, build: str) -> models.Patch | None:
        stmt = select(models.Patch).where(models.Patch.build == build)
        patch = self.session.scalar(stmt)
        return patch

    def get_seen(self) -> typing.Collection[models.Patch]:
        return self.seen_tracker.get_all()


class SqlDeviceRepository(DeviceRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[models.Device]
    ) -> None:
        super().__init__()
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, device: models.Device) -> None:
        self.session.add(device)
        self.seen_tracker.add(device)

    def add_or_update(self, device_dicts: PreparedValues) -> None:
        # TODO: Should I use seen_tracker here?
        stmt = insert(models.Device).values(device_dicts)
        stmt = stmt.on_conflict_do_update(
            index_elements=[models.Device.identifier],
            set_={
                "name": stmt.excluded.name,
                "identifier": stmt.excluded.identifier,
                "models": stmt.excluded.models,
                "released": stmt.excluded.released,
                "discontinued": stmt.excluded.discontinued,
                "hardware_info": stmt.excluded.hardware_info,
            },
        )
        self.session.execute(stmt)

    def get(self, identifier: str) -> models.Device | None:
        stmt = select(models.Device).where(models.Device.identifier == identifier)
        device = self.session.scalar(stmt)
        return device

    def get_seen(self) -> typing.Collection[models.Device]:
        return self.seen_tracker.get_all()


class SqlManufacturerRepository(ManufacturerRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[models.Manufacturer]
    ) -> None:
        super().__init__()
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, manufacturer: models.Manufacturer) -> None:
        self.session.add(manufacturer)
        self.seen_tracker.add(manufacturer)

    def get(self, name: str) -> models.Manufacturer | None:
        stmt = select(models.Manufacturer).where(models.Manufacturer.name == name)
        manufacturer = self.session.scalar(stmt)
        return manufacturer

    def get_seen(self) -> typing.Collection[models.Manufacturer]:
        return self.seen_tracker.get_all()


class SqlCVERepository(CVERepository):
    def __init__(self, session: Session, seen_tracker: SeenTracker[models.CVE]) -> None:
        super().__init__()
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, patch: models.CVE) -> None:
        self.session.add(patch)
        self.seen_tracker.add(patch)

    def add_or_update(self, cve_dicts: PreparedValues) -> None:
        stmt = insert(models.CVE).values(cve_dicts)
        stmt = stmt.on_conflict_do_update(
            index_elements=[models.CVE.cve_id],
            set_={
                "description": stmt.excluded.description,
                "published": stmt.excluded.published,
                "last_modified": stmt.excluded.last_modified,
                "cvss": stmt.excluded.cvss,
            },
        )
        self.session.execute(stmt)

    def get(self, cve_id: str) -> models.CVE | None:
        stmt = select(models.CVE).where(models.CVE.cve_id == cve_id)
        patch = self.session.scalar(stmt)
        return patch

    def get_seen(self) -> typing.Collection[models.CVE]:
        return self.seen_tracker.get_all()


class SqlCWERepository(CWERepository):
    def __init__(self, session: Session, seen_tracker: SeenTracker[models.CWE]) -> None:
        super().__init__()
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, cwe: models.CWE) -> None:
        self.session.add(cwe)
        self.seen_tracker.add(cwe)

    def add_or_update(self, cwe_dicts: PreparedValues) -> None:
        stmt = insert(models.CWE).values(cwe_dicts)
        stmt = stmt.on_conflict_do_update(
            index_elements=[models.CWE.cwe_id],  # type: ignore
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
        )
        self.session.execute(stmt)

    def get(self, cwe_id: int) -> models.CWE | None:
        stmt = select(models.CWE).where(models.CWE.cwe_id == cwe_id)
        cwe = self.session.scalar(stmt)
        return cwe

    def get_seen(self) -> typing.Collection[models.CWE]:
        return self.seen_tracker.get_all()


class SqlCAPECRepository(CAPECRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[models.CAPEC]
    ) -> None:
        super().__init__()
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, capec: models.CAPEC) -> None:
        self.session.add(capec)
        self.seen_tracker.add(capec)

    def add_or_update(self, capec_dicts: PreparedValues) -> None:
        stmt = insert(models.CAPEC).values(capec_dicts)
        stmt = stmt.on_conflict_do_update(
            index_elements=[models.CAPEC.capec_id],  # type: ignore
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
        )
        self.session.execute(stmt)

    def get(self, capec_id: int) -> models.CAPEC | None:
        stmt = select(models.CAPEC).where(models.CAPEC.capec_id == capec_id)
        capec = self.session.scalar(stmt)
        return capec

    def get_seen(self) -> typing.Collection[models.CAPEC]:
        return self.seen_tracker.get_all()
