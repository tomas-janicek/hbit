#! /usr/bin/env bash

# Let the DB start
python /hbit_api/api/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python /hbit_api/api/initial_data.py
