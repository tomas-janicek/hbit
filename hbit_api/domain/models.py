import datetime
import typing
from dataclasses import dataclass, field

from sqlalchemy.orm import Mapped

from hbit_api.domain import events as domain_events
from hbit_api.domain.dto import devices as devices_dto


@dataclass
class User:
    email: Mapped[str]
    name: Mapped[str | None]
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = True  # type: ignore
    is_superuser: Mapped[bool] = False  # type: ignore
    id: Mapped[int | None] = None  # type: ignore

    events: list[domain_events.Event] = field(default_factory=list)

    def __new__(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Self:
        obj = super().__new__(cls)
        obj.events = []
        return obj

    def send_verification_email(self) -> None:
        send_new_account_email = domain_events.NotifyNewAccount(email=self.email)
        self.events.append(send_new_account_email)

    def send_password_recovery_email(self) -> None:
        send_new_account_email = domain_events.NotifyRecoverPassword(email=self.email)
        self.events.append(send_new_account_email)

    def __hash__(self) -> int:
        return hash(self.email)

    def dict(self) -> dict[str, typing.Any]:
        return {
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
        }


@dataclass
class CAPEC:
    capec_id: Mapped[int]
    description: Mapped[str]
    extended_description: Mapped[str]
    likelihood_of_attack: Mapped[str]
    severity: Mapped[str]
    execution_flow: Mapped[list[dict[str, typing.Any]]]
    prerequisites: Mapped[list[str]]
    skills_required: Mapped[list[dict[str, typing.Any]]]
    resources_required: Mapped[list[str]]
    consequences: Mapped[list[str]]
    id: Mapped[int | None] = None  # type: ignore

    events: list[domain_events.Event] = field(default_factory=list)

    def __new__(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Self:
        obj = super().__new__(cls)
        obj.events = []
        return obj

    def __hash__(self) -> int:
        return hash(self.capec_id)

    def dict(self) -> dict[str, typing.Any]:
        return {
            "capec_id": self.capec_id,
            "description": self.description,
            "extended_description": self.extended_description,
            "likelihood_of_attack": self.likelihood_of_attack,
            "severity": self.severity,
            "execution_flow": self.execution_flow,
            "prerequisites": self.prerequisites,
            "skills_required": self.skills_required,
            "resources_required": self.resources_required,
            "consequences": self.consequences,
        }


@dataclass
class CWE:
    cwe_id: Mapped[int]
    name: Mapped[str]
    description: Mapped[str]
    extended_description: Mapped[str]
    likelihood_of_exploit: Mapped[str]
    background_details: Mapped[list[str]]
    potential_mitigations: Mapped[list[dict[str, typing.Any]]]
    detection_methods: Mapped[list[dict[str, typing.Any]]]
    capecs: Mapped[list[CAPEC]]
    id: Mapped[int | None] = None  # type: ignore

    events: list[domain_events.Event] = field(default_factory=list)

    def __new__(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Self:
        obj = super().__new__(cls)
        obj.events = []
        return obj

    def __hash__(self) -> int:
        return hash(self.cwe_id)

    def dict(self) -> dict[str, typing.Any]:
        return {
            "cwe_id": self.cwe_id,
            "name": self.name,
            "description": self.description,
            "extended_description": self.extended_description,
            "likelihood_of_exploit": self.likelihood_of_exploit,
            "background_details": self.background_details,
            "potential_mitigations": self.potential_mitigations,
            "detection_methods": self.detection_methods,
        }


@dataclass
class CVE:
    cve_id: Mapped[str]
    description: Mapped[str]
    published: Mapped[datetime.datetime]
    last_modified: Mapped[datetime.datetime]
    cvss: Mapped[dict[str, typing.Any]]
    cwes: Mapped[list[CWE]]
    patches: Mapped[list["Patch"]]
    id: Mapped[int | None] = None  # type: ignore

    events: list[domain_events.Event] = field(default_factory=list)

    def __new__(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Self:
        obj = super().__new__(cls)
        obj.events = []
        return obj

    def __hash__(self) -> int:
        return hash(self.cve_id)

    def dict(self) -> dict[str, typing.Any]:
        return {
            "cve_id": self.cve_id,
            "description": self.description,
            "published": self.published,
            "last_modified": self.last_modified,
            "cvss": self.cvss,
        }


@dataclass
class Manufacturer:
    name: Mapped[str]
    id: Mapped[int | None] = None  # type: ignore

    events: list[domain_events.Event] = field(default_factory=list)

    def __new__(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Self:
        obj = super().__new__(cls)
        obj.events = []
        return obj

    def __hash__(self) -> int:
        return hash(self.name)

    def dict(self) -> dict[str, typing.Any]:
        return {"name": self.name}


@dataclass
class Device:
    manufacturer: Mapped[Manufacturer]
    name: Mapped[str]
    identifier: Mapped[str]
    models: Mapped[list[str]]
    released: Mapped[datetime.date | None]
    discontinued: Mapped[datetime.date | None]
    hardware_info: Mapped[devices_dto.HardwareInfo]
    id: Mapped[int | None] = None  # type: ignore

    events: list[domain_events.Event] = field(default_factory=list)

    def __new__(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Self:
        obj = super().__new__(cls)
        obj.events = []
        return obj

    def __hash__(self) -> int:
        return hash(self.identifier)

    def dict(self) -> dict[str, typing.Any]:
        return {
            "name": self.name,
            "identifier": self.identifier,
            "models": self.models,
            "released": self.released,
            "discontinued": self.discontinued,
            "hardware_info": self.hardware_info,
        }


@dataclass
class Patch:
    build: Mapped[str]
    os: Mapped[str]
    name: Mapped[str]
    version: Mapped[str]
    major: Mapped[int]
    minor: Mapped[int]
    patch: Mapped[int]
    released: Mapped[datetime.date | None]
    cves: Mapped[list[CVE]]
    devices: Mapped[list[Device]]
    id: Mapped[int | None] = None  # type: ignore

    events: list[domain_events.Event] = field(default_factory=list)

    def __new__(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Self:
        obj = super().__new__(cls)
        obj.events = []
        return obj

    def __hash__(self) -> int:
        return hash(self.build)

    def dict(self) -> dict[str, typing.Any]:
        return {
            "build": self.build,
            "os": self.os,
            "name": self.name,
            "version": self.version,
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "released": self.released,
        }
