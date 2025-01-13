from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_groq import ChatGroq

from hbit import settings

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.075,  # one request in 4 seconds
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

code_model_name = "mixtral-8x7b-32768"
code_model = ChatGroq(
    model=code_model_name,
    temperature=0,
    seed=settings.MODEL_SEED,  # type: ignore
    rate_limiter=rate_limiter,
)

smaller_model_name = "llama-3.1-8b-instant"
smaller_model_name = "llama3-8b-8192"
smaller_model = ChatGroq(
    model=smaller_model_name,
    temperature=0,
    seed=settings.MODEL_SEED,  # type: ignore
    rate_limiter=rate_limiter,
)
