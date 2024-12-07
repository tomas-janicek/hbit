from sqlalchemy import create_engine

from hbit_api.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
