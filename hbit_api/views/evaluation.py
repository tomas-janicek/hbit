from sqlalchemy.orm import Session
from sqlmodel import select

from hbit_api import errors
from hbit_api.domain import models
from hbit_api.domain.dto import evaluation as dto


def read_evaluation(
    session: Session,
    device_identifier: str,
    patch_build: str,
) -> dto.EvaluationDto:
    statement = select(models.Device).where(
        models.Device.identifier == device_identifier
    )
    device = session.scalar(statement)

    if not device:
        raise errors.DoesNotExist()

    statement = (
        select(models.Patch)
        .where(models.Patch.build == patch_build)
        .join(models.Patch.devices)  # type: ignore
        .where(models.Device.id == device.id)
    )
    patch = session.scalar(statement)

    if not patch:
        raise errors.DoesNotExist()

    device_evaluation = dto.EvaluationDto.from_device_and_patch(device, patch)
    return device_evaluation
