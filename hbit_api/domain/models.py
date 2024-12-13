import datetime
import typing
from dataclasses import dataclass, field

from hbit_api.domain import events

if typing.TYPE_CHECKING:
    from hbit_api.domain.dto import devices as devices_dto
    from hbit_api.domain.dto import vuls as vuls_dto


@dataclass
class User:
    email: str
    name: str | None
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
        return hash(self.email)


@dataclass
class CAPEC:
    capec_id: int
    description: str
    extended_description: str
    likelihood_of_attack: str
    severity: str
    execution_flow: list["vuls_dto.AttackStepDto"]
    prerequisites: list[str]
    skills_required: list["vuls_dto.SkillDto"]
    resources_required: list[str]
    consequences: list[str]
    id: int | None = None

    events: list["events.Event"] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.capec_id)


@dataclass
class CWE:
    cwe_id: int
    name: str
    description: str
    extended_description: str
    likelihood_of_exploit: str
    background_details: list[str]
    potential_mitigations: list["vuls_dto.MitigationDto"]
    detection_methods: list["vuls_dto.DetectionMethodDto"]
    capecs: list[CAPEC]
    id: int | None = None

    events: list["events.Event"] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.cwe_id)


@dataclass
class CVE:
    cve_id: str
    description: str
    published: datetime.datetime
    last_modified: datetime.datetime
    cvss: "vuls_dto.CVSSDto"
    cwes: list[CWE]
    id: int | None = None

    events: list["events.Event"] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.cve_id)


@dataclass
class Manufacturer:
    name: str
    id: int | None = None

    events: list["events.Event"] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Device:
    manufacturer: Manufacturer
    name: str
    identifier: str
    models: list[str]
    released: datetime.date | None
    discontinued: datetime.date | None
    hardware_info: "devices_dto.HardwareInfo"
    id: int | None = None

    events: list["events.Event"] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.identifier)


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

    events: list["events.Event"] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.build)
