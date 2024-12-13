import typing

import pydantic

from hbit_data import clients, config, dto, processors

ItemT = typing.TypeVar("ItemT")


class CWEHBITPipeline(processors.Pipeline[dto.CWE]):
    def __init__(self, hbit_client: clients.HBITClient) -> None:
        self.hbit_client = hbit_client

    def process_batch(self, items: list[dto.CWE]) -> None:
        if not items:
            return
        self.hbit_client.send_cwes(items)

    def end_processing(self) -> None: ...


class SecurityUpdatesHBITPipeline(processors.Pipeline[dto.SecurityUpdate]):
    def __init__(self, hbit_client: clients.HBITClient) -> None:
        self.hbit_client = hbit_client

    def process_batch(self, items: list[dto.SecurityUpdate]) -> None:
        if not items:
            return
        self.hbit_client.send_security_updates(items)

    def end_processing(self) -> None: ...


class PatchesHBITPipeline(processors.Pipeline[dto.Patch]):
    def __init__(self, hbit_client: clients.HBITClient) -> None:
        self.hbit_client = hbit_client

    def process_batch(self, items: list[dto.Patch]) -> None:
        if not items:
            return
        self.hbit_client.send_patches(items)

    def end_processing(self) -> None: ...


class CVEHBITPipeline(processors.Pipeline[dto.CVE]):
    def __init__(self, hbit_client: clients.HBITClient, patch_build: str) -> None:
        self.hbit_client = hbit_client
        self.patch_build = patch_build

    def process_batch(self, items: list[dto.CVE]) -> None:
        if not items:
            return
        self.hbit_client.send_cves(self.patch_build, items)

    def end_processing(self) -> None: ...


class CAPECHBITPipeline(processors.Pipeline[dto.CAPEC]):
    def __init__(self, hbit_client: clients.HBITClient) -> None:
        self.hbit_client = hbit_client

    def process_batch(self, items: list[dto.CAPEC]) -> None:
        if not items:
            return
        self.hbit_client.send_capecs(items)

    def end_processing(self) -> None: ...


class JSONDumpPipeline(processors.Pipeline[ItemT]):
    def __init__(self, file: str) -> None:
        self.processed_items: list[ItemT] = []
        self.file_path = config.BASE_DIR / "data" / file

    def process_batch(self, items: list[ItemT]) -> None:
        self.processed_items.extend(items)

    def end_processing(self) -> None:
        type_adapter = pydantic.TypeAdapter(list[ItemT])
        items_json = type_adapter.dump_json(self.processed_items)
        with open(self.file_path, "w+b") as f:
            f.write(items_json)
