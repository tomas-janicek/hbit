import json
import typing

from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine

from hbit.config import settings


def _custom_json_serializer(*args: typing.Any, **kwargs: typing.Any) -> str:
    """
    Encodes json in the same way that pydantic does.
    """
    return json.dumps(*args, default=jsonable_encoder, **kwargs)


engine = create_engine(
    settings.READ_SQLALCHEMY_DATABASE_URI, json_serializer=_custom_json_serializer
)

__all__ = ["engine"]
