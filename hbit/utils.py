import random
import string

import httpx
from authlib.integrations.httpx_client import OAuth2Client  # type: ignore
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel

from common import utils
from hbit import services, settings


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


def generate_random_string(length: int = 10) -> str:
    """Generate a random string of given length using letters and digits."""
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


def get_registry_from_config(config: RunnableConfig) -> services.ServiceContainer:
    registry = config.get("configurable", {}).get("registry", None)
    if not registry:
        raise RuntimeError(
            "Error in tool / model configuration. Registry must be part of RunnableConfig!"
        )

    return registry


def utf8_length(text: str) -> int:
    return len(text.encode("utf-8"))
