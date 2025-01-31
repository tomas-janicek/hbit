import typing

from langchain_anthropic import ChatAnthropic
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_openai import ChatOpenAI
from langchain_together import ChatTogether
from langgraph.checkpoint.memory import MemorySaver

from common import requests
from hbit import (
    clients,
    core,
    enums,
    evaluations,
    extractors,
    prompting,
    services,
    settings,
    summaries,
    types,
    utils,
)
from hbit.evaluations import device_evaluations, patch_evaluations
from hbit.extractors import device_extractors, patch_extractors
from hbit.prompting import chat_prompting, general_prompting


def create_services(
    device_extractor_type: enums.DeviceExtractorType,
    patch_extractor_type: enums.PatchExtractorType,
    device_evaluation_type: enums.DeviceEvaluationType,
    patch_evaluation_type: enums.PatchEvaluationType,
    summary_service_type: enums.SummaryServiceType,
    model_provider: enums.ModelProvider = enums.ModelProvider.OPEN_AI,
) -> services.ServiceContainer:
    service_factory = ServicesFactory()

    service_factory.add_db()
    service_factory.add_requests()
    service_factory.add_client()

    # TODO: Move this logic to service factory
    match model_provider:
        case enums.ModelProvider.GROQ:
            service_factory.add_models()
            service_factory.add_chat_prompt_templates()
        case enums.ModelProvider.OPEN_AI:
            service_factory.add_openai_models()
            service_factory.add_chat_prompt_templates()
        case enums.ModelProvider.ANTHROPIC:
            service_factory.add_anthropic_models()
            service_factory.add_chat_prompt_templates()
        case enums.ModelProvider.DEEPSEEK:
            service_factory.add_deepseek_models()
            service_factory.add_chat_prompt_templates()
        case enums.ModelProvider.GOOGLE:
            service_factory.add_google_models()
            service_factory.add_chat_prompt_templates()
        case enums.ModelProvider.MISTRAL:
            service_factory.add_mistral_models()
            service_factory.add_chat_prompt_templates()
        case enums.ModelProvider.TOGETHER_AI:
            service_factory.add_together_ai_models()
            service_factory.add_chat_prompt_templates()

    service_factory.add_saver()
    service_factory.add_device_extractor(device_extractor_type)
    service_factory.add_patch_extractor(patch_extractor_type)
    service_factory.add_device_evaluation_service(device_evaluation_type)
    service_factory.add_patch_evaluation_service(patch_evaluation_type)
    service_factory.add_summary_service(summary_service_type)

    return service_factory.registry


class ServicesFactory:
    def __init__(self):
        self.registry = services.ServiceContainer()

    def add_models(
        self, requests_per_second: float = settings.REQUESTS_PER_SECOND
    ) -> typing.Self:
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=requests_per_second,
            check_every_n_seconds=requests_per_second / 10,
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
        self.registry.register_service(types.ExtractionModel, code_model)
        self.registry.register_service(types.AgentModel, code_model)
        return self

    def add_openai_models(
        self, requests_per_second: float = settings.REQUESTS_PER_SECOND
    ) -> typing.Self:
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=requests_per_second,
            check_every_n_seconds=requests_per_second / 10,
            max_bucket_size=1,
        )

        default_model_name = "gpt-4o"
        default_model = ChatOpenAI(
            model=default_model_name,
            temperature=0,
            seed=settings.MODEL_SEED,
            rate_limiter=rate_limiter,
        )

        small_model_name = "gpt-4o-mini"
        small_model = ChatOpenAI(
            model=small_model_name,
            temperature=0,
            seed=settings.MODEL_SEED,
            rate_limiter=rate_limiter,
        )

        self.registry.register_service(types.DefaultModel, default_model)
        self.registry.register_service(types.CodeModel, small_model)
        self.registry.register_service(types.SmallModel, small_model)
        self.registry.register_service(types.ExtractionModel, small_model)
        self.registry.register_service(types.AgentModel, default_model)
        return self

    def add_anthropic_models(
        self, requests_per_second: float = settings.REQUESTS_PER_SECOND
    ) -> typing.Self:
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=requests_per_second,
            check_every_n_seconds=requests_per_second / 10,
            max_bucket_size=1,
        )

        default_model_name = "claude-3-5-sonnet-latest"
        default_model = ChatAnthropic(
            model=default_model_name,  # type: ignore
            temperature=0,
            rate_limiter=rate_limiter,
        )
        small_model_name = "claude-3-haiku-20240307"
        small_model = ChatAnthropic(
            model=small_model_name,  # type: ignore
            temperature=0,
            rate_limiter=rate_limiter,
        )
        code_model_name = "claude-3-5-sonnet-latest"
        code_model = ChatAnthropic(
            model=code_model_name,  # type: ignore
            temperature=0,
            rate_limiter=rate_limiter,
        )

        self.registry.register_service(types.DefaultModel, default_model)
        self.registry.register_service(types.CodeModel, code_model)
        self.registry.register_service(types.SmallModel, small_model)
        self.registry.register_service(types.ExtractionModel, code_model)
        self.registry.register_service(types.AgentModel, default_model)
        return self

    def add_mistral_models(
        self, requests_per_second: float = settings.REQUESTS_PER_SECOND
    ) -> typing.Self:
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=requests_per_second,
            check_every_n_seconds=requests_per_second / 10,
            max_bucket_size=1,
        )

        default_model_name = "mistral-large-latest"
        default_model = ChatMistralAI(
            model=default_model_name,  # type: ignore
            temperature=0,
            rate_limiter=rate_limiter,
        )
        small_model_name = "mistral-small-latest"
        small_model = ChatMistralAI(
            model=small_model_name,  # type: ignore
            temperature=0,
            rate_limiter=rate_limiter,
        )
        code_model_name = "codestral-latest"
        code_model = ChatMistralAI(
            model=code_model_name,  # type: ignore
            temperature=0,
            rate_limiter=rate_limiter,
        )

        self.registry.register_service(types.DefaultModel, default_model)
        self.registry.register_service(types.CodeModel, code_model)
        self.registry.register_service(types.SmallModel, small_model)
        self.registry.register_service(types.ExtractionModel, code_model)
        self.registry.register_service(types.AgentModel, default_model)
        return self

    def add_deepseek_models(
        self, requests_per_second: float = settings.REQUESTS_PER_SECOND
    ) -> typing.Self:
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=requests_per_second,
            check_every_n_seconds=requests_per_second / 10,
            max_bucket_size=1,
        )

        default_model_name = "deepseek-chat"
        default_model = ChatAnthropic(
            model=default_model_name,  # type: ignore
            temperature=0,
            seed=settings.MODEL_SEED,  # type: ignore
            rate_limiter=rate_limiter,
        )
        code_model_name = "deepseek-reasoner"
        code_model = ChatGroq(
            model=code_model_name,
            temperature=0,
            seed=settings.MODEL_SEED,  # type: ignore
            rate_limiter=rate_limiter,
        )

        self.registry.register_service(types.DefaultModel, default_model)
        self.registry.register_service(types.CodeModel, code_model)
        self.registry.register_service(types.SmallModel, default_model)
        self.registry.register_service(types.ExtractionModel, default_model)
        self.registry.register_service(types.AgentModel, default_model)
        return self

    def add_google_models(
        self, requests_per_second: float = settings.REQUESTS_PER_SECOND
    ) -> typing.Self:
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=requests_per_second,
            check_every_n_seconds=requests_per_second / 10,
            max_bucket_size=1,
        )

        default_model_name = "gemini-1.5-pro"
        default_model = ChatGoogleGenerativeAI(
            model=default_model_name,
            temperature=0,
            seed=settings.MODEL_SEED,  # type: ignore
            rate_limiter=rate_limiter,
        )

        small_model_name = "gemini-2.0-flash-exp"
        small_model = ChatGoogleGenerativeAI(
            model=small_model_name,
            temperature=0,
            seed=settings.MODEL_SEED,  # type: ignore
            rate_limiter=rate_limiter,
        )

        self.registry.register_service(types.DefaultModel, default_model)
        self.registry.register_service(types.CodeModel, default_model)
        self.registry.register_service(types.SmallModel, small_model)
        self.registry.register_service(types.ExtractionModel, small_model)
        self.registry.register_service(types.AgentModel, default_model)
        return self

    def add_together_ai_models(
        self, requests_per_second: float = settings.REQUESTS_PER_SECOND
    ) -> typing.Self:
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=requests_per_second,
            check_every_n_seconds=requests_per_second / 10,
            max_bucket_size=1,
        )

        default_model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
        default_model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
        default_model = ChatTogether(
            model=default_model_name,
            temperature=0,
            seed=settings.MODEL_SEED,
            rate_limiter=rate_limiter,
        )

        self.registry.register_service(types.DefaultModel, default_model)
        self.registry.register_service(types.CodeModel, default_model)
        self.registry.register_service(types.SmallModel, default_model)
        self.registry.register_service(types.ExtractionModel, default_model)
        self.registry.register_service(types.AgentModel, default_model)
        return self

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

    def add_device_evaluation_service(
        self, type: enums.DeviceEvaluationType
    ) -> typing.Self:
        client = self.registry.get_service(clients.HBITClient)

        match type:
            case enums.DeviceEvaluationType.IMPERATIVE:
                evaluation_service = device_evaluations.IterativeEvaluationService(
                    client
                )
            case enums.DeviceEvaluationType.AI:
                code_model = self.registry.get_service(types.CodeModel)
                prompt_store = self.registry.get_service(prompting.PromptStore)
                evaluation_service = device_evaluations.AiDeviceEvaluationService(
                    code_model, prompt_store, client
                )

        self.registry.register_service(
            evaluations.DeviceEvaluationService, evaluation_service
        )
        return self

    def add_patch_evaluation_service(
        self, type: enums.PatchEvaluationType
    ) -> typing.Self:
        client = self.registry.get_service(clients.HBITClient)

        match type:
            case enums.PatchEvaluationType.IMPERATIVE:
                evaluation_service = patch_evaluations.IterativePatchEvaluationService(
                    client
                )
            case enums.PatchEvaluationType.AI:
                code_model = self.registry.get_service(types.CodeModel)
                prompt_store = self.registry.get_service(prompting.PromptStore)
                evaluation_service = patch_evaluations.AiPatchEvaluationService(
                    code_model, prompt_store, client
                )

        self.registry.register_service(
            evaluations.PatchEvaluationService, evaluation_service
        )
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
