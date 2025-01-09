import typing

from pydantic import BaseModel


class QueryOutput(BaseModel):
    """Generated SQL query."""

    query: typing.Annotated[str, ..., "Syntactically valid SQL query."]
