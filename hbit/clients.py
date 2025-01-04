from hbit_api.domain.dto.evaluation import EvaluationDto
from hbit_data import requests


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
        )
        return evaluation
