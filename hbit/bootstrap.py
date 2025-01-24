import typing

from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_groq import ChatGroq

from common import requests
from hbit import (
    clients,
    core,
    enums,
    evaluations,
    extractors,
    services,
    settings,
    summaries,
    types,
    utils,
)
from hbit.extractors import device_extractors, patch_extractors


class ServicesFactory:
    def __init__(self):
        self.registry = services.ServiceContainer()

    def add_models(self) -> typing.Self:
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=0.05,
            check_every_n_seconds=0.5,
            max_bucket_size=1,
        )

        default_model_name = "llama3-70b-8192"
        default_model = ChatGroq(
            model=default_model_name,
            temperature=0,
            seed=settings.MODEL_SEED,  # type: ignore
            rate_limiter=rate_limiter,
        )

        code_model_name = "llama-3.3-70b-versatile"
        code_model = ChatGroq(
            model=code_model_name,
            temperature=0,
            seed=settings.MODEL_SEED,  # type: ignore
            rate_limiter=rate_limiter,
        )

        smaller_model_name = "llama-3.1-8b-instant"
        smaller_model = ChatGroq(
            model=smaller_model_name,
            temperature=0,
            seed=settings.MODEL_SEED,  # type: ignore
            rate_limiter=rate_limiter,
        )

        self.registry.register_service(types.DefaultModel, default_model)
        self.registry.register_service(types.CodeModel, code_model)
        self.registry.register_service(types.SmallModel, smaller_model)
        return self

    def add_db(self) -> typing.Self:
        db = core.DatabaseService()

        self.registry.register_service(core.DatabaseService, db)
        return self

    def add_requests(self) -> typing.Self:
        request = requests.HTTPXRequests(utils.create_hbit_api_client())

        self.registry.register_service(requests.Requests, request)
        return self

    def add_client(self) -> typing.Self:
        request = self.registry.get_service(requests.Requests)

        client = clients.ApiHBITClient(request, settings.HBIT_API_URL)

        self.registry.register_service(clients.HBITClient, client)
        return self

    def add_device_extractor(self, type: enums.DeviceExtractorType) -> typing.Self:
        default_model = self.registry.get_service(types.DefaultModel)
        db = self.registry.get_service(core.DatabaseService)

        match type:
            case enums.DeviceExtractorType.SQL_EXTRACTOR:
                device_extractor = device_extractors.StructureDeviceExtractor(
                    model=default_model, db=db
                )
            case enums.DeviceExtractorType.STRUCTURED_EXTRACTOR:
                device_extractor = device_extractors.SqlDeviceExtractor(
                    model=default_model, db=db
                )

        self.registry.register_service(extractors.DeviceExtractor, device_extractor)
        return self

    def add_patch_extractor(self, type: enums.PatchExtractorType) -> typing.Self:
        default_model = self.registry.get_service(types.DefaultModel)
        db = self.registry.get_service(core.DatabaseService)

        match type:
            case enums.PatchExtractorType.SQL_EXTRACTOR:
                patch_extractor = patch_extractors.StructurePatchExtractor(
                    model=default_model, db=db
                )
            case enums.PatchExtractorType.STRUCTURED_EXTRACTOR:
                patch_extractor = patch_extractors.SqlPatchExtractor(
                    model=default_model, db=db
                )

        self.registry.register_service(extractors.PatchExtractor, patch_extractor)
        return self

    def add_evaluation_service(self, type: enums.EvaluationServiceType) -> typing.Self:
        client = self.registry.get_service(clients.HBITClient)

        match type:
            case enums.EvaluationServiceType.IMPERATIVE:
                evaluation_service = evaluations.IterativeEvaluationService(client)
            case enums.EvaluationServiceType.AI:
                code_model = self.registry.get_service(types.CodeModel)
                evaluation_service = evaluations.AiEvaluationService(code_model, client)

        self.registry.register_service(
            evaluations.EvaluationService, evaluation_service
        )
        return self

    def add_summary_service(self, type: enums.SummaryServiceType) -> typing.Self:
        default_model = self.registry.get_service(types.DefaultModel)
        small_model = self.registry.get_service(types.SmallModel)

        match type:
            case enums.SummaryServiceType.AI:
                summary_service = summaries.AiSummaryService(
                    summary_model=small_model, analysis_model=default_model
                )

        self.registry.register_service(summaries.SummaryService, summary_service)
        return self


def create_services(
    device_extractor_type: enums.DeviceExtractorType,
    patch_extractor_type: enums.PatchExtractorType,
    evaluation_service_type: enums.EvaluationServiceType,
    summary_service_type: enums.SummaryServiceType,
) -> services.ServiceContainer:
    service_factory = ServicesFactory()

    service_factory.add_db()
    service_factory.add_requests()
    service_factory.add_client()
    service_factory.add_models()
    service_factory.add_device_extractor(device_extractor_type)
    service_factory.add_patch_extractor(patch_extractor_type)
    service_factory.add_evaluation_service(evaluation_service_type)
    service_factory.add_summary_service(summary_service_type)

    return service_factory.registry
