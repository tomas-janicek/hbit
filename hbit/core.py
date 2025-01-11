import json
import typing

import sqlalchemy
from fastapi.encoders import jsonable_encoder
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine

from hbit.config import settings


def _custom_json_serializer(*args: typing.Any, **kwargs: typing.Any) -> str:
    """
    Encodes json in the same way that pydantic does.
    """
    return json.dumps(*args, default=jsonable_encoder, **kwargs)


class DatabaseService:
    def __init__(self, url: str = settings.READ_SQLALCHEMY_DATABASE_URI) -> None:
        self.engine = create_engine(url, json_serializer=_custom_json_serializer)
        self.db_tool = SQLDatabase(engine=self.engine, sample_rows_in_table_info=7)
        self.dialect = self.db_tool.dialect

    def get_table_info(self, table_names: list[str] | None = None) -> str:
        return self.db_tool.get_table_info(table_names)

    def connect(self) -> sqlalchemy.Connection:
        return self.engine.connect()
