import typing

from langchain.text_splitter import RecursiveCharacterTextSplitter

from hbit import (
    core,
    services,
    settings,
    types,
    utils,
)


class VectorDBFactory:
    def __init__(self, registry: services.ServiceContainer) -> None:
        self.registry = registry

    def add_vector_db(self) -> typing.Self:
        db = core.VectorService()

        self.registry.register_service(core.VectorService, db)
        return self

    def add_text_splitter(self) -> typing.Self:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE - settings.CHUNK_OVERLAP,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=utils.utf8_length,
        )

        self.registry.register_service(types.TextSplitter, splitter)
        return self
