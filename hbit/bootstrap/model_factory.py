import typing

from langchain_anthropic import ChatAnthropic
from langchain_core.rate_limiters import BaseRateLimiter, InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
from langchain_together import ChatTogether

from hbit import enums, prompting, services, settings, types
from hbit.prompting import chat_prompting, general_prompting


class ModelServiceFactory:
    def __init__(
        self,
        registry: services.ServiceContainer,
        requests_per_second: float = settings.REQUESTS_PER_SECOND,
    ) -> None:
        self.registry = registry
        self.requests_per_second = requests_per_second

    def add_models(self, model_provider: enums.ModelProvider) -> None:
        match model_provider:
            case enums.ModelProvider.GROQ:
                self.add_groq_models()
                self.add_chat_prompt_templates()
            case enums.ModelProvider.OPEN_AI:
                self.add_openai_models()
                self.add_chat_prompt_templates()
            case enums.ModelProvider.ANTHROPIC:
                self.add_anthropic_models()
                self.add_chat_prompt_templates()
            case enums.ModelProvider.GOOGLE:
                self.add_google_models()
                self.add_chat_prompt_templates()
            case enums.ModelProvider.MISTRAL:
                self.add_mistral_models()
                self.add_chat_prompt_templates()
            case enums.ModelProvider.TOGETHER_AI:
                self.add_together_ai_models()
                self.add_chat_prompt_templates()
            case enums.ModelProvider.NVIDIA:
                self.add_nvidia_models()
                self.add_chat_prompt_templates()

    def add_general_prompt_templates(self) -> typing.Self:
        prompt_store = general_prompting.GeneralPromptStore()
        self.registry.register_service(prompting.PromptStore, prompt_store)
        return self

    def add_chat_prompt_templates(self) -> typing.Self:
        prompt_store = chat_prompting.ChatPromptStore()
        self.registry.register_service(prompting.PromptStore, prompt_store)
        return self

    def add_groq_models(self) -> typing.Self:
        rate_limiter = self._create_rate_limiter()

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

    def add_openai_models(self) -> typing.Self:
        rate_limiter = self._create_rate_limiter()

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

    def add_anthropic_models(self) -> typing.Self:
        rate_limiter = self._create_rate_limiter()

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

    def add_mistral_models(self) -> typing.Self:
        rate_limiter = self._create_rate_limiter()

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

    def add_google_models(self) -> typing.Self:
        rate_limiter = self._create_rate_limiter()

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

    def add_together_ai_models(self) -> typing.Self:
        rate_limiter = self._create_rate_limiter()

        default_model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
        default_model = ChatTogether(
            model=default_model_name,
            temperature=0,
            seed=settings.MODEL_SEED,
            rate_limiter=rate_limiter,
        )

        small_model_name = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
        small_model = ChatTogether(
            model=small_model_name,
            temperature=0,
            seed=settings.MODEL_SEED,
            rate_limiter=rate_limiter,
        )

        self.registry.register_service(types.DefaultModel, default_model)
        self.registry.register_service(types.CodeModel, small_model)
        self.registry.register_service(types.SmallModel, small_model)
        self.registry.register_service(types.ExtractionModel, default_model)
        self.registry.register_service(types.AgentModel, default_model)
        return self

    def add_nvidia_models(self) -> typing.Self:
        rate_limiter = self._create_rate_limiter()

        default_model_name = "meta/llama-3.3-70b-instruct"
        default_model = ChatNVIDIA(
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

    def _create_rate_limiter(self) -> BaseRateLimiter:
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=self.requests_per_second,
            check_every_n_seconds=self.requests_per_second / 10,
            max_bucket_size=1,
        )
        return rate_limiter
