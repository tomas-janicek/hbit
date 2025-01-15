import typing
from collections.abc import Iterator

from common import requests
from hbit_data import dto, settings

from . import base


class iPhoneScraper(base.Scraper[dto.Device]):
    def __init__(self, request: requests.Requests) -> None:
        self.request = request
        self.apple_db = "https://api.appledb.dev"
        self.devices_path = "/device/main.json"

    def scrape(self) -> Iterator[dto.Device]:
        data = self.request.get_or_retry(
            base=self.apple_db,
            path=self.devices_path,
            response_type=list[dict[str, typing.Any]],
            timeout=settings.DEFAULT_TIMEOUT,
        )
        if not data:
            raise Exception(f"Error loading iPhones from {self.apple_db}.")

        for raw_device in data:
            if not self._is_wanted_device(raw_device):
                continue

            hw_info = dto.HardwareInfo(
                arch=raw_device.get("arch"),  # type: ignore
                boards=raw_device.get("board"),  # type: ignore
                soc=raw_device.get("soc"),  # type: ignore
            )
            iphone = dto.Device(
                manufacturer="apple",
                name=raw_device.get("name"),  # type: ignore
                identifier=raw_device.get("key"),  # type: ignore
                models=raw_device.get("model"),  # type: ignore
                released=self._create_released(raw_device),  # type: ignore
                discontinued=raw_device.get("discontinued"),
                hardware_info=hw_info,
            )

            yield iphone

    def _is_wanted_device(self, device: dict[str, typing.Any]) -> bool:
        type = device.get("type", "").lower()
        if type != "iphone":
            return False

        return True

    def _create_released(self, device: dict[str, typing.Any]) -> str | None:
        released = device.get("released")
        match released:
            case str():
                return released
            case list():
                return released[0]  # type: ignore
            case _:
                return None
