from common import requests
from hbit import settings

# TODO: Move this to common or copy it here
from hbit_api.domain.dto.evaluation import EvaluationDto


class HBITClient:
    def __init__(self, request: requests.Requests, hbit_api_url: str) -> None:
        self.request = request
        self.hbit_api_url = hbit_api_url

    def get_device_evaluation(
        self, device_identifier: str, patch_build: str
    ) -> EvaluationDto | None:
        evaluation = self.request.get(
            base=self.hbit_api_url,
            path=f"device-evaluation?device_identifier={device_identifier}&patch_build={patch_build}",
            response_type=EvaluationDto,
            timeout=settings.DEFAULT_TIMEOUT,
        )
        return evaluation
