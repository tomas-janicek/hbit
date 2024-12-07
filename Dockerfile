FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /hbit_api/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /hbit_api/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

ENV PYTHONPATH=/hbit_api

COPY ./scripts/ /hbit_api/

COPY ./alembic.ini /hbit_api/

COPY ./prestart.sh /hbit_api/

COPY ./tests-start.sh /hbit_api/

COPY ./hbit_api /hbit_api
