import svcs
from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from hbit_api.api import deps
from hbit_api.domain import events
from hbit_api.domain.dto import generic as generic_dto
from hbit_api.service_layer import messagebus

router = APIRouter()


@router.post(
    "/test-email",
    dependencies=[Depends(deps.get_current_active_superuser)],
    status_code=201,
)
def test_email(
    services: svcs.fastapi.DepContainer, email_to: EmailStr
) -> generic_dto.Message:
    """
    Test emails.
    """
    bus = services.get(messagebus.MessageBus)
    test_notify = events.TestNotify(email=email_to)
    bus.handle(test_notify)
    return generic_dto.Message(message="Test email sent")
