from sqlalchemy.orm import Session, selectinload
from sqlmodel import select

from common import dto as common_dto
from hbit_api import errors
from hbit_api.domain import models


def read_device_evaluation(
    session: Session,
    device_identifier: str,
    patch_build: str,
) -> common_dto.DeviceEvaluationDto:
    statement = (
        select(models.Device)
        .where(models.Device.identifier.like(device_identifier))
        .options(selectinload(models.Device.manufacturer))
    )
    device = session.scalar(statement)

    if not device:
        raise errors.DoesNotExist("Provided device identifier is invalid.")

    statement = (
        select(models.Patch)
        .where(models.Patch.build.like(patch_build))
        .join(models.Patch.devices)
        .where(models.Device.id == device.id)
        .options(
            selectinload(models.Patch.cves)
            .selectinload(models.CVE.cwes)
            .selectinload(models.CWE.capecs),
        )
    )
    patch = session.scalar(statement)

    if not patch:
        raise errors.DoesNotExist("Provided patch build is invalid.")

    device_evaluation = common_dto.DeviceEvaluationDto.from_device_and_patch(
        device, patch
    )
    return device_evaluation


def read_patch_evaluation(
    session: Session, patch_build: str
) -> common_dto.PatchEvaluationDto:
    statement = (
        select(models.Patch)
        .where(models.Patch.build.like(patch_build))
        .options(
            selectinload(models.Patch.cves)
            .selectinload(models.CVE.cwes)
            .selectinload(models.CWE.capecs),
        )
    )
    patch = session.scalar(statement)

    if not patch:
        raise errors.DoesNotExist()

    device_evaluation = common_dto.PatchEvaluationDto.from_patch(patch)
    return device_evaluation
