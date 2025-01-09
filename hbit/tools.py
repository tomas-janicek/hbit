from langchain_core.tools import tool  # type: ignore

from common import dto as common_dto
from common import requests
from hbit import clients, settings


@tool
def get_device_vulnerabilities(
    device_identifier: str, patch_name: str
) -> common_dto.EvaluationDto | None:
    """Get the vulnerabilities of a device."""
    request = requests.Requests()
    hbit_client = clients.ApiHBITClient(
        request=request, hbit_api_url=settings.HBIT_API_URL
    )
    vulnerabilities = hbit_client.get_device_evaluation(device_identifier, patch_name)
    return vulnerabilities
