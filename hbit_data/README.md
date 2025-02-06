#  HBIT Data

This repository contains the data models and scrapers for handling various 
security-related data, including CVEs, CWEs, CAPECs, and patches.

## 📁 Directory Structure

- `scrapers/`: Contains scrapers for different security data sources.
- `scripts/`: Contains scripts for downloading data.
- `data/`: Directory where downloaded data files are stored.
- `tests/`: Test for HBIT data project.
- `cli.py`: Command-line interface for interacting with the data project.
- `clients.py`: Contains client implementations for external services.
- `config`: Configuration settings and management.
- `dto.py`: Contains data transfer objects (DTOs) for various security entities.
- `enums.py`: Enum classes.
- `normalizer.py`: Functions and classes for normalizing data.
- `pipelines.py`: Data processing pipelines.
- `processors.py`: Service logic that combines logic of scrapers and pipelines.
- `utils.py`: General utility functions.

## 📐 Architecture

### Item Processor

`ItemProcessor` is cental point of application. It uses pipelines and given scraper and 
scrapes items using scraper class and then processes these items calling all pre-configure
pipelines on scraped items. Because `ItemProcessor` can taky any number of pipelines, it can be 
configured to precess items in different way. CLI configures Item processor to send save 
scraped items into JSON file in `data/` directory and send them to HBIT API. Pipeline `JSONDumpPipeline`
is used to save items to JSON. Every item type has it's own pipeline (`*HBITPipeline`, 
for example `PatchesHBITPipeline`) that send item given type to specific endpoint in HBIT API.

### HBIT Client

TBD

### Scrapers

TBD

## 🎲 Design Decision

TBD

### Why did I create so many interfaces?

TBD

### Why is `Requests` interface separate from `HBITClient`?

TBD

### What is the advantage of pipelines and why is't this logic part of `ItemProcessor`?

TBD

### Why is typing and using Pydantic classes so important for this project?

TBD

## 🚀 Next Steps

## 💿 Data Models

TBD

### CVE

```py
class CVE(BaseModel):
        cve_id: str
        description: str
        published: datetime
        last_modified: datetime
        cvss: CVSS
        cwe_ids: list[int]
```

### CWE

```py
class CWE(BaseModel):
        cwe_id: int
        name: StripedStr
        description: StripedStr
        extended_description: StripedStr
        likelihood_of_exploit: LoweredString
        background_details: list[StripedStr]
        potential_mitigations: list[Mitigation]
        detection_methods: list[DetectionMethod]
```

### CAPEC

```py
class CAPEC(BaseModel):
        capec_id: int
        description: StripedStr
        extended_description: StripedStr
        likelihood_of_attack: LoweredString
        severity: LoweredString
        execution_flow: list[AttackStep]
        prerequisites: list[StripedStr]
        skills_required: list[Skill]
        resources_required: list[StripedStr]
        consequences: list[StripedStr]
        cwe_ids: list[int]
```

### Patch

```py
class Patch(BaseModel):
        os: enums.Os
        name: str
        version: str
        major: int
        minor: int
        patch: int
        build: str
        released: datetime
```

## 🌐 Scrapers

### CWEScraper

Scrapes CWE data from the MITRE CWE database.

### CAPECScraper

Scrapes CAPEC data from the MITRE CAPEC database.

### CVEScraper

Scrapes CVE data from the NVD database.

### PatchScraper

Scrapes patch data from the Apple database.

### SecurityUpdateScraper

TBD

## ⚒️ Usage

Before running scrapers, download CAPECs and CWEs data. This data will 
be used by their respective scrapers.

```sh
bash hbit_data/scripts/download_capecs.sh
bash hbit_data/scripts/download_cwes.sh
```

Run scrapers:

```sh
PYTHONPATH=. python hbit_data/cli.py scrape_cwes
PYTHONPATH=. python hbit_data/cli.py scrape_capecs
PYTHONPATH=. python hbit_data/cli.py scrape_patches
PYTHONPATH=. python hbit_data/cli.py scrape_security_updates
PYTHONPATH=. python hbit_data/cli.py scrape_iphones
```


## ⚙️ Scripts

### download_capecs.sh

Downloads the latest CAPEC data from MITRE.

### download_cwes.sh

Downloads the latest CWE data from MITRE.
