import svcs
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from common import dto as common_dto
from hbit_api.api import deps
from hbit_api.views import evaluation as views

router = APIRouter()


@router.get(
    "/device-evaluation",
    response_model=common_dto.DeviceEvaluationDto,
)
def read_device_evaluation(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    device_identifier: str,
    patch_build: str,
) -> common_dto.DeviceEvaluationDto:
    """
    Retrieve device evaluation details.
    """
    session = services.get(Session)

    try:
        device_evaluation = views.read_device_evaluation(
            session, device_identifier, patch_build
        )
    except views.errors.DoesNotExist as error:
        raise HTTPException(
            status_code=404,
            detail=f"Device evaluation not found. {error!s}",
        )
    return device_evaluation


@router.get(
    "/patch-evaluation",
    response_model=common_dto.PatchEvaluationDto,
)
def read_patch_evaluation(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    patch_build: str,
) -> common_dto.PatchEvaluationDto:
    """
    Retrieve patch evaluation details.
    """
    session = services.get(Session)

    try:
        patch_evaluation = views.read_patch_evaluation(session, patch_build)
    except views.errors.DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Patch evaluation not found. Provided patch build is invalid.",
        )
    return patch_evaluation
