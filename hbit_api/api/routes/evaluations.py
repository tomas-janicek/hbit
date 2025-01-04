import svcs
from fastapi import APIRouter
from sqlalchemy.orm import Session

from hbit_api.api import deps
from hbit_api.domain.dto import evaluation as dto
from hbit_api.views import evaluation as views

router = APIRouter()


@router.get(
    "/device-evaluation",
    response_model=dto.EvaluationDto,
)
def read_device_evaluation(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    device_identifier: str,
    patch_build: str,
) -> dto.EvaluationDto:
    """
    Retrieve device evaluation details.
    """
    session = services.get(Session)

    device_evaluation = views.read_evaluation(session, device_identifier, patch_build)
    return device_evaluation
