from sqlalchemy.orm import Session
from sqlmodel import select

from common import dto as common_dto
from hbit_api import errors
from hbit_api.domain import models


def read_device_evaluation(
    session: Session,
    device_identifier: str,
    patch_build: str,
) -> common_dto.DeviceEvaluationDto:
    statement = select(models.Device).where(
        models.Device.identifier.like(device_identifier)
    )
    device = session.scalar(statement)

    if not device:
        raise errors.DoesNotExist()

    statement = (
        select(models.Patch)
        .where(models.Patch.build.like(patch_build))
        .join(models.Patch.devices)
        .where(models.Device.id == device.id)
    )
    patch = session.scalar(statement)

    if not patch:
        raise errors.DoesNotExist()

    device_evaluation = common_dto.DeviceEvaluationDto.from_device_and_patch(
        device, patch
    )
    return device_evaluation


def read_patch_evaluation(
    session: Session, patch_build: str
) -> common_dto.PatchEvaluationDto:
    statement = select(models.Patch).where(models.Patch.build.like(patch_build))
    patch = session.scalar(statement)

    if not patch:
        raise errors.DoesNotExist()

    device_evaluation = common_dto.PatchEvaluationDto.from_patch(patch)
    return device_evaluation
