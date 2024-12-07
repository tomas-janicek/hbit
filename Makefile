.PHONY: make-migrations migrate format lint

make-migrations:
	source .env && PYTHONPATH=. alembic revision --autogenerate -m $(m)

migrate:
	source .env && PYTHONPATH=. alembic upgrade head

init_db:
	source .env && PYTHONPATH=. python hbit_api/cli.py init_db_data

format:
	ruff format

lint: 
	ruff check --fix
