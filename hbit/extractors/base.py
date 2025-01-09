import typing


class DeviceExtractor(typing.Protocol):
    def extract_device_identifier(self, text: str) -> str | None: ...


class PatchExtractor(typing.Protocol):
    def extract_patch_build(self, text: str) -> str | None: ...
