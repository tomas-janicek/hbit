import httpx
from authlib.integrations.httpx_client import OAuth2Client  # type: ignore

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
