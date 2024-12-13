import json
import typing

from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from hbit_api.core.config import settings


def _custom_json_serializer(*args: typing.Any, **kwargs: typing.Any) -> str:
    """
    Encodes json in the same way that pydantic does.
    """
    return json.dumps(*args, default=jsonable_encoder, **kwargs)


engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), json_serializer=_custom_json_serializer
)


def ping_db(session: Session) -> None:
    session.execute(select(1))
