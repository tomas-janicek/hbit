import logging.config

from hbit.config import LOGGING, settings

logging.config.dictConfig(config=LOGGING)

__all__ = ["settings"]
