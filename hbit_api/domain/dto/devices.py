import datetime

from pydantic import BaseModel


class HardwareInfo(BaseModel):
    arch: str
    boards: list[str]
    soc: str


class DeviceDto(BaseModel):
    manufacturer: str
    name: str
    identifier: str
    models: list[str]
    released: datetime.date | None
    discontinued: datetime.date | None
    hardware_info: HardwareInfo
