from sqlalchemy.orm import Session
from sqlmodel import select

from common import dto as common_dto
from hbit_api import errors
from hbit_api.domain import models


def read_evaluation(
    session: Session,
    device_identifier: str,
    patch_build: str,
) -> common_dto.EvaluationDto:
    statement = select(models.Device).where(
        models.Device.identifier.like(device_identifier)  # type: ignore
    )
    device = session.scalar(statement)

    if not device:
        raise errors.DoesNotExist()

    statement = (
        select(models.Patch)
        .where(models.Patch.build.like(patch_build))  # type: ignore
        .join(models.Patch.devices)  # type: ignore
        .where(models.Device.id == device.id)
    )
    patch = session.scalar(statement)

    if not patch:
        raise errors.DoesNotExist()

    device_evaluation = common_dto.EvaluationDto.from_device_and_patch(device, patch)
    return device_evaluation
