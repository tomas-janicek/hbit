import typing

from hbit_data import dto, enums, normalizer, requests

from . import base


class PatchScraper(base.Scraper[dto.Patch]):
    def __init__(self, request: requests.Requests) -> None:
        self.request = request
        self.apple_db = "https://api.appledb.dev"
        self.ios_pacthes_path = "/ios/iOS/main.json"
        self.min_version = normalizer.VersionStr.normalize_version("15.0.0")

    def scrape(self) -> typing.Iterator[dto.Patch]:
        data = self.request.get(
            base=self.apple_db,
            path=self.ios_pacthes_path,
            response_type=list[dict[str, typing.Any]],
        )
        if not data:
            raise Exception(f"Error loading iOS data from {self.apple_db}.")

        for raw_patch in data:
            version = normalizer.Version.validate_python(raw_patch.get("version"))

            if not self._is_wanted_patch(raw_patch, version):
                continue

            released = raw_patch.get("released")
            patch = dto.Patch(
                os=enums.Os.IOS,
                name=raw_patch.get("version"),  # type: ignore
                version=version,
                major=version.major,
                minor=version.minor,
                patch=version.patch,
                build=raw_patch.get("build"),  # type: ignore
                released=released if released else None,
                affected_devices=raw_patch.get("deviceMap"),  # type: ignore
            )

            yield patch

    def _is_wanted_patch(
        self, raw_patch: dict[str, typing.Any], version: normalizer.VersionStr
    ) -> bool:
        # TODO: Write comment why this is important (because getting patch CVE is very lengthy)
        if raw_patch.get("osStr", "").lower() != "ios":
            return False
        if raw_patch.get("beta") or raw_patch.get("rc") or raw_patch.get("rsr"):
            return False
        if "simulator" in raw_patch.get("version", "").lower():
            return False
        if "sdk" in raw_patch.get("version", "").lower():
            return False
        if version <= self.min_version:
            return False
        return True
