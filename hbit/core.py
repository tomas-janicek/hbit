import json
import typing

import sqlalchemy
from fastapi.encoders import jsonable_encoder
from langchain_community.utilities.sql_database import SQLDatabase
from pymilvus import (  # type: ignore
    CollectionSchema,
    DataType,
    FieldSchema,
    MilvusClient,
)
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


class VectorService:
    def __init__(
        self,
        uri: str = settings.VECTOR_DB_URI,
        collection_name: str = "security_papers",
    ) -> None:
        self.uri = uri
        self.client = MilvusClient(uri=self.uri, token="root:Milvus", timeout=5)
        self.collection_name = collection_name

    def create_database(self, db_name: str) -> None:
        self.client.create_database(db_name=db_name)

    def re_create_security_papers(self) -> None:
        self.client.drop_collection(self.collection_name)
        self.create_security_papers()

    def create_security_papers(self) -> None:
        id_schema = FieldSchema(
            name="id", dtype=DataType.INT64, is_primary=True, auto_id=True
        )
        vector_schema = FieldSchema(
            name="vector",
            dtype=DataType.FLOAT_VECTOR,
            # The dimension of the embedding vector.
            # This MUST match the output of your embedding model.
            dim=settings.EMBEDDING_SIZE,
        )
        text_schema = FieldSchema(
            name="text",
            dtype=DataType.VARCHAR,
            # Note that multibyte characters (e.g., Unicode characters) may occupy more
            # than one byte each, so ensure the byte length of inserted strings does not
            # exceed the specified limit.
            max_length=settings.CHUNK_SIZE,
        )
        category_schema = FieldSchema(
            name="category", dtype=DataType.VARCHAR, max_length=100
        )

        schema = CollectionSchema(
            fields=[id_schema, vector_schema, text_schema, category_schema]
        )

        index_params = MilvusClient.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            metric_type="COSINE",
            index_type="IVF_FLAT",
            index_name="vector_index",
            params={"nlist": 128},
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params,
        )
