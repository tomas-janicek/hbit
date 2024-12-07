.PHONY: make-migrations migrate format lint

make-migrations:
	alembic revision --autogenerate -m $(m)

migrate:
	source .env && PYTHONPATH=. alembic upgrade head

# TODO: Write this correctly with CLI
init_db:
	source .env && PYTHONPATH=. python hbit_api/initial_data.py

format:
	ruff format

lint: 
	ruff check --fix
