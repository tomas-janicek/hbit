import svcs
from fastapi import APIRouter
from starlette import status

from hbit_api.api import deps
from hbit_api.domain import commands
from hbit_api.domain.dto import devices as dto
from hbit_api.service_layer import messagebus

router = APIRouter()


# TODO: Add exception hadlers


@router.post(
    "/batch",
)
def create_device_batch(
    services: svcs.fastapi.DepContainer,
    super_user: deps.CurrentSuperUser,
    device_batch: list[dto.DeviceDto],
) -> int:
    """
    Create batch of Devices.
    """
    bus = services.get(messagebus.MessageBus)

    create_devices = commands.CreateDevices(device_batch=device_batch)
    bus.handle(message=create_devices)
    return status.HTTP_201_CREATED
