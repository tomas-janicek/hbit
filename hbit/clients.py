from common import dto as common_dto
from common import requests
from hbit import settings


class HBITClient:
    def get_device_evaluation(
        self, device_identifier: str, patch_build: str
    ) -> common_dto.DeviceEvaluationDto: ...

    def get_patch_evaluation(
        self, patch_build: str
    ) -> common_dto.PatchEvaluationDto: ...

    def get_cves(self, patch_build: str | None = None) -> common_dto.CVEsDto: ...


class ApiHBITClient(HBITClient):
    def __init__(self, request: requests.Requests, hbit_api_url: str) -> None:
        self.request = request
        self.hbit_api_url = hbit_api_url

    def get_device_evaluation(
        self, device_identifier: str, patch_build: str
    ) -> common_dto.DeviceEvaluationDto:
        evaluation = self.request.get(
            base=self.hbit_api_url,
            path=f"device-evaluation?device_identifier={device_identifier}&patch_build={patch_build}",
            response_type=common_dto.DeviceEvaluationDto,
            timeout=settings.DEFAULT_TIMEOUT,
        )
        return evaluation

    def get_patch_evaluation(self, patch_build: str) -> common_dto.PatchEvaluationDto:
        evaluation = self.request.get(
            base=self.hbit_api_url,
            path=f"patch-evaluation?patch_build={patch_build}",
            response_type=common_dto.PatchEvaluationDto,
            timeout=settings.DEFAULT_TIMEOUT,
        )
        return evaluation

    def get_cves(self, patch_build: str | None = None) -> common_dto.CVEsDto:
        cves = self.request.get(
            base=self.hbit_api_url,
            path=f"cves?patch_build={patch_build}",
            response_type=common_dto.CVEsDto,
            timeout=settings.DEFAULT_TIMEOUT,
            params={"patch_build": patch_build},
        )
        return cves
