import typing

from hbit import core, dto, services, types


class SecurityPapersService:
    def __init__(
        self,
        registry: services.ServiceContainer,
        collection_name: str = "security_papers",
    ) -> None:
        self.registry = registry
        self.db_service = self.registry.get_service(core.VectorService)
        self.db = self.db_service.client
        self.embeddings_model = self.registry.get_service(types.EmbeddingModel)
        self.splitter = self.registry.get_service(types.TextSplitter)
        self.collection_name = collection_name

    def save_text(self, security_paper: dto.SecurityPaper) -> None:
        data = self._create_insert_data(security_paper)
        self.db.insert(collection_name=self.collection_name, data=data)

    def save_texts(self, security_papers: typing.Iterable[dto.SecurityPaper]) -> None:
        data: list[dict[str, typing.Any]] = []
        for paper in security_papers:
            data.extend(self._create_insert_data(paper))

        self.db.insert(
            collection_name=self.collection_name,
            data=data,
        )

    def query_vector_db(
        self, query: str, query_filters: dto.SecurityPaperQuery, n_results: int = 5
    ) -> list[dto.SecurityPaperResponse]:
        query_vector = self.embeddings_model.embed_query(query)

        # TODO: Can I create context manager for this?
        self.db.load_collection(collection_name=self.collection_name)

        queries_results: list[list[dict[str, typing.Any]]] = self.db.search(
            collection_name=self.collection_name,
            anns_field="vector",
            data=[query_vector],
            limit=n_results,
            # TODO: Create filtering expression from query dto and use it here
            # expr=f"category == {category.value}",
            output_fields=["text", "category"],
        )

        self.db.release_collection(collection_name=self.collection_name)

        return [
            dto.SecurityPaperResponse(
                distance=result["distance"],
                security_paper=dto.SecurityPaper(
                    text=result["entity"]["text"], category=result["entity"]["category"]
                ),
            )
            for queries_result in queries_results
            for result in queries_result
        ]

    def get_collection_info(self) -> dict[str, typing.Any]:
        collection_info: dict[str, typing.Any] = self.db.describe_collection(  # type: ignore
            collection_name=self.collection_name
        )
        indexes: list[str] = self.db.list_indexes(collection_name=self.collection_name)
        return {"collection_info": collection_info, "indexes": indexes}

    def _create_insert_data(
        self, security_paper: dto.SecurityPaper
    ) -> list[dict[str, typing.Any]]:
        chunks = self.splitter.split_text(security_paper.text)
        embeddings = self.embeddings_model.embed_documents(chunks)

        insert_data = [
            {
                "category": security_paper.category,
                "vector": embedding,
                "text": chunk,
            }
            for chunk, embedding in zip(chunks, embeddings, strict=False)
        ]

        return insert_data
