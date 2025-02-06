# HBIT Project

HBIT is a project aimed at analyzing and aggregating security information 
about mobile devices. It consists of several components including scrapers, 
a web API, and a CLI application. Below is an overview of the project's structure 
and functionality.

## Project Structure

### 1. Scrapers

The scrapers gather data from various sources and store it in a structured format. The main scrapers include:

- **Security Updates Scraper**: Collects security updates.
- **iPhones Scraper**: Gathers information about iPhone models.
- **CWEs Scraper**: Collects Common Weakness Enumerations.
- **CAPECs Scraper**: Collects Common Attack Pattern Enumeration and Classification.
- **Patches Scraper**: Collects patch information.

### 2. Web API

The web API provides access to the collected data. It is built using FastAPI and includes endpoints for:

- **Login**: User authentication.
- **Users**: User management.
- **Devices**: Device information.
- **Vulnerabilities**: Vulnerability information.
- **Evaluations**: Security evaluations of devices and patches.

### 3. AI UI

TBD


## Installation

To install the project, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/TomasJani/hbit.git
    cd hbit
    ```

2. Install the dependencies:
    ```sh
    uv sync
    ```

## Usage

### Creating `.env` file

The project uses environment variables for configuration. 
Create a `.env` file in the root directory. You can use 
`.env.example` as and example and fill every `change-this`.

Some env variables are set to `change-one-of`. You will be 
required to fill at least one env variable in group of this 
variables.


### Starting the REST API

To start the REST API, run:

```sh
uvicorn hbit_api.api.main:api_router --reload
```

### Running the Scrapers

> [!WARNING]
> Running scrapers requires having HBIT API running.

You can ran all scrapers in correct order calling bash script:

```sh
bash hbit_data/scripts/run_scrapers.sh
```

To run individual the scrapers, use the CLI commands provided in `hbit_data/cli.py`. 
For example, to scrape security updates:

```sh
PYTHONPATH=. python hbit_data/cli.py scrape_security_updates
```

### Streamlit AI UI

To use the CLI application, run:
```sh
PYTHONPATH=. python -m streamlit run hbit/ui/security_agent.py
```
