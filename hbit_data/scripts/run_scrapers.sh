#!/usr/bin/env bash

set -e

bash hbit_data/scripts/download_capecs.sh
bash hbit_data/scripts/download_cwes.sh

export PYTHONPATH=. 

python hbit_data/cli.py scrape_cwes
python hbit_data/cli.py scrape_capecs
python hbit_data/cli.py scrape_security_updates
python hbit_data/cli.py scrape_iphones
