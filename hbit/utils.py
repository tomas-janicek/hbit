import httpx
from authlib.integrations.httpx_client import OAuth2Client  # type: ignore
from pydantic import BaseModel

from common import utils
from hbit import settings


def create_hbit_api_client() -> httpx.Client:
    client = OAuth2Client()

    token_endpoint = utils.create_url(
        base=settings.HBIT_API_URL, path="/login/access-token"
    )
    client.fetch_token(
        token_endpoint,
        username=settings.ADMIN_EMAIL,
        password=settings.ADMIN_PASSWORD,
    )
    return client


def are_all_fields_none(model: BaseModel) -> bool:
    return all(value is None for value in model.model_dump().values())
