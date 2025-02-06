#!/usr/bin/env bash

set -e

bash hbit_data/scripts/download_capecs.sh
bash hbit_data/scripts/download_cwes.sh

export PYTHONPATH=. 

echo "Scrape CWEs"
uv run hbit_data/cli.py scrape_cwes

echo "Scrape CAPECs"
uv run hbit_data/cli.py scrape_capecs

echo "Scrape Security Updates"
uv run hbit_data/cli.py scrape_security_updates

echo "Scrape Security iPhones"
uv run hbit_data/cli.py scrape_iphones
