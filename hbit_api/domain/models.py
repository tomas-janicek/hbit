import datetime
import typing
from dataclasses import dataclass, field

from hbit_api.domain import events as domain_events
from hbit_api.domain.dto import devices as devices_dto


@dataclass
class User:
    email: str
    name: str | None
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    id: int | None = None

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
    capec_id: int
    description: str
    extended_description: str
    likelihood_of_attack: str
    severity: str
    execution_flow: list[dict[str, typing.Any]]
    prerequisites: list[str]
    skills_required: list[dict[str, typing.Any]]
    resources_required: list[str]
    consequences: list[str]
    id: int | None = None

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
    cwe_id: int
    name: str
    description: str
    extended_description: str
    likelihood_of_exploit: str
    background_details: list[str]
    potential_mitigations: list[dict[str, typing.Any]]
    detection_methods: list[dict[str, typing.Any]]
    capecs: list[CAPEC]
    id: int | None = None

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
    cve_id: str
    description: str
    published: datetime.datetime
    last_modified: datetime.datetime
    cvss: dict[str, typing.Any]
    cwes: list[CWE]
    id: int | None = None

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
    name: str
    id: int | None = None

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
    manufacturer: Manufacturer
    name: str
    identifier: str
    models: list[str]
    released: datetime.date | None
    discontinued: datetime.date | None
    hardware_info: devices_dto.HardwareInfo
    id: int | None = None

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
    build: str
    os: str
    name: str
    version: str
    major: int
    minor: int
    patch: int
    released: datetime.date | None
    cves: list[CVE]
    devices: list[Device]
    id: int | None = None

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
