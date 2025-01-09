import svcs
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from common import dto as common_dto
from hbit_api.api import deps
from hbit_api.views import evaluation as views

router = APIRouter()


@router.get(
    "/device-evaluation",
    response_model=common_dto.EvaluationDto,
)
def read_device_evaluation(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    device_identifier: str,
    patch_build: str,
) -> common_dto.EvaluationDto:
    """
    Retrieve device evaluation details.
    """
    session = services.get(Session)

    try:
        device_evaluation = views.read_evaluation(
            session, device_identifier, patch_build
        )
    except views.errors.DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Evaluation not found. Combination of patch build and device identifier is invalid.",
        )
    return device_evaluation
