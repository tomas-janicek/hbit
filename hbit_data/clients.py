import logging

import pydantic

from hbit_data import dto, requests

_log = logging.getLogger(__name__)


class HBITClient:
    def __init__(self, request: requests.Requests, hbit_api_url: str) -> None:
        self.request = request
        self.hbit_api_url = hbit_api_url

    def send_security_updates(self, security_updates: list[dto.SecurityUpdate]) -> None:
        patches = [su.patch for su in security_updates]
        self.send_patches(patches)

        for security_update in security_updates:
            self.send_cves(security_update.patch.build, security_update.cves)

    def send_patches(self, patches: list[dto.Patch]) -> None:
        patches_adapter = pydantic.TypeAdapter(list[dto.Patch])
        self.request.post(
            base=self.hbit_api_url,
            path="/patches/batch",
            content=patches_adapter.dump_json(patches),
        )

    def send_cves(self, patch_build: str, cves: list[dto.CVE]) -> None:
        cve_adapter = pydantic.TypeAdapter(list[dto.CVE])
        self.request.post(
            base=self.hbit_api_url,
            path=f"/patches/{patch_build}/cves/batch",
            content=cve_adapter.dump_json(cves),
        )

    def send_cwes(self, cwes: list[dto.CWE]) -> None:
        cwes_adapter = pydantic.TypeAdapter(list[dto.CWE])
        self.request.post(
            base=self.hbit_api_url,
            path="/cwes/batch",
            content=cwes_adapter.dump_json(cwes),
        )

    def send_capecs(self, capecs: list[dto.CAPEC]) -> None:
        capecs_adapter = pydantic.TypeAdapter(list[dto.CAPEC])
        self.request.post(
            base=self.hbit_api_url,
            path="/capecs/batch",
            content=capecs_adapter.dump_json(capecs),
        )
