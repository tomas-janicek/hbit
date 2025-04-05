import typing

from langchain.text_splitter import TextSplitter
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver

SmallModel = typing.NewType("SmallModel", BaseChatModel)
CodeModel = typing.NewType("CodeModel", BaseChatModel)
DefaultModel = typing.NewType("DefaultModel", BaseChatModel)
ExtractionModel = typing.NewType("ExtractionModel", BaseChatModel)
AgentModel = typing.NewType("AgentModel", BaseChatModel)
EmbeddingModel = typing.NewType("EmbeddingModel", Embeddings)
Splitter = typing.NewType("Splitter", TextSplitter)

Saver = typing.NewType("Saver", MemorySaver)
