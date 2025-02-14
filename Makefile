.PHONY: make-migrations migrate init_db format lint detect-secrets

make-migrations:
	PYTHONPATH=. uv run alembic revision --autogenerate -m $(m)

migrate:
	PYTHONPATH=. uv run alembic upgrade head

init_db:
	PYTHONPATH=. uv run hbit_api/cli.py init_db_data

format:
	ruff format

lint: 
	ruff check --fix

detect-secrets:
	ggshield secret scan repo .
