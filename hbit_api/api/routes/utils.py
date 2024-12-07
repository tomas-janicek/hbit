from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from hbit_api import utils
from hbit_api.api import deps
from hbit_api.domain.dto import generic as generic_dto

router = APIRouter()


@router.post(
    "/test-email/",
    dependencies=[Depends(deps.get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> generic_dto.Message:
    """
    Test emails.
    """
    email_data = utils.generate_test_email(email_to=email_to)
    utils.send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return generic_dto.Message(message="Test email sent")
