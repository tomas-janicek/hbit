import typing

from langgraph.checkpoint.memory import MemorySaver

from common import requests
from hbit import (
    clients,
    core,
    enums,
    extractors,
    prompting,
    services,
    settings,
    summaries,
    types,
    utils,
)
from hbit.extractors import device_extractors, patch_extractors
from hbit.prompting import chat_prompting, general_prompting


class ServicesFactory:
    def __init__(self, registry: services.ServiceContainer) -> None:
        self.registry = registry

    def add_general_prompt_templates(self) -> typing.Self:
        prompt_store = general_prompting.GeneralPromptStore()
        self.registry.register_service(prompting.PromptStore, prompt_store)
        return self

    def add_chat_prompt_templates(self) -> typing.Self:
        prompt_store = chat_prompting.ChatPromptStore()
        self.registry.register_service(prompting.PromptStore, prompt_store)
        return self

    def add_saver(self) -> typing.Self:
        saver = MemorySaver()
        self.registry.register_service(types.Saver, saver)

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
        default_model = self.registry.get_service(types.ExtractionModel)
        db = self.registry.get_service(core.DatabaseService)
        prompt_store = self.registry.get_service(prompting.PromptStore)

        match type:
            case enums.DeviceExtractorType.JSON:
                device_extractor = device_extractors.JsonDeviceExtractor(
                    model=default_model, db=db, prompt_store=prompt_store
                )
            case enums.DeviceExtractorType.SQL:
                device_extractor = device_extractors.SqlDeviceExtractor(
                    model=default_model, db=db, prompt_store=prompt_store
                )

        self.registry.register_service(extractors.DeviceExtractor, device_extractor)
        return self

    def add_patch_extractor(self, type: enums.PatchExtractorType) -> typing.Self:
        default_model = self.registry.get_service(types.ExtractionModel)
        db = self.registry.get_service(core.DatabaseService)
        prompt_store = self.registry.get_service(prompting.PromptStore)

        match type:
            case enums.PatchExtractorType.JSON:
                patch_extractor = patch_extractors.JsonPatchExtractor(
                    model=default_model, db=db, prompt_store=prompt_store
                )
            case enums.PatchExtractorType.SQL:
                patch_extractor = patch_extractors.SqlPatchExtractor(
                    model=default_model, db=db, prompt_store=prompt_store
                )

        self.registry.register_service(extractors.PatchExtractor, patch_extractor)
        return self

    def add_summary_service(self, type: enums.SummaryServiceType) -> typing.Self:
        default_model = self.registry.get_service(types.DefaultModel)
        small_model = self.registry.get_service(types.SmallModel)
        prompt_store = self.registry.get_service(prompting.PromptStore)

        match type:
            case enums.SummaryServiceType.AI:
                summary_service = summaries.AiSummaryService(
                    summary_model=small_model,
                    analysis_model=default_model,
                    prompt_store=prompt_store,
                )

        self.registry.register_service(summaries.SummaryService, summary_service)
        return self
