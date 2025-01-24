import typing

from langchain_core.language_models import BaseChatModel

SmallModel = typing.NewType("SmallModel", BaseChatModel)
CodeModel = typing.NewType("CodeModel", BaseChatModel)
DefaultModel = typing.NewType("DefaultModel", BaseChatModel)
