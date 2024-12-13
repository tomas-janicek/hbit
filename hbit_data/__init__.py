import logging.config

from hbit_data.config import LOGGING, settings

logging.config.dictConfig(config=LOGGING)

__all__ = ["settings"]
