#  HBIT Data

This repository contains the data models and scrapers for handling various 
security-related data, including *CVEs*, *CWEs*, *CAPECs*, and *patches*.

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

### 🛠️ Item Processor

`ItemProcessor` is the *central point* of the application. It uses pipelines and a given scraper to scrape items using the scraper class and then processes these items by calling all pre-configured pipelines on the scraped items. Because `ItemProcessor` can take any number of pipelines, it can be configured to process items in different ways. The CLI configures the Item processor to save scraped items into a JSON file in the `data/` directory and send them to the HBIT API. The pipeline `JSONDumpPipeline` is used to save items to JSON. Every item type has its own pipeline (`*HBITPipeline`, for example, `PatchesHBITPipeline`) that sends items of a given type to a specific endpoint in the HBIT API.

### 🌐 HBIT Client

`HBITClient` takes care of all communication with the HBIT API. It has separate functions for every endpoint used to send data to the HBIT API.

### 🕷️ Scrapers

All scrapers implement a very simple interface exposing only the `scrape(self) -> typing.Iterator[ItemT]` function. This enables us to link the scraper with the item DTO through the generic variable *ItemT*. Thus, the processor, pipelines, and scrapers all know which scraped item they will work with, and all of these classes can be implemented to work on all item classes through generic variables.

I took advantage of this generic variable when implementing pipelines. `*HBITPipeline` pipelines are specific to every item type because they need to be sent to a specific endpoint, but `JSONDumpPipeline` can be used with all scraped items.

## 🎲 Design Decision

This section provides simple explanations of why I went with certain maybe unconventional design decisions for this kind of project.

### 🤔 Why did I create so many interfaces in such a simple project?

For *testing*. Using interfaces in constructors and arguments enables me to use "fake" classes in their place to test only specific behavior/classes.

For example, by having a `Scraper` interface, I can create a fake scraper that always returns a dict. I can use this fake scraper when testing `ItemProcessor`. When something fails, I know the problem must be part of `ItemProcessor` because the fake scraper will have a dummy return statement.

### 🔄 Why is the `Requests` interface separate from `HBITClient`?

For *testing*. In this case, it's even more important to have these two classes separate than in the example above. When testing `HBITClient`, I don't want to have the HBIT API up and running. I want to create a fake requests class that saves request information clients want to send and checks if `HBITClient` sets them correctly.

> [!IMPORTANT]
> For specific end-to-end tests, there should be tests of communication between HBIT Data and the HBIT API. However, these tests should only test communication, and `HBITClient` should have separate tests for its logic.

### 🔌 What is the advantage of pipelines and why isn't this logic part of `ItemProcessor`?

I can easily plug in new behavior. For example, if the infrastructure changes to using Kafka for communication, I can just create a new pipeline that sends this data differently.

### 📝 Why is typing and using Pydantic classes so important for this project?

Scrapers take data from external sources. I can never be sure that this data will follow a certain schema and will never change. Pydantic can help me easily validate types and sometimes the semantic value of scraped data.

## 🚀 Next Steps

1) Write tests. I already created files for services that really need tests.
These services orchestrate high-level behavior, and if they do not work correctly, nothing would work.
2) Add support for Android devices and Android patches.
3) Use async/threading to optimize scrapers. This will be useful when I add Android devices. There are a lot more Android devices, and it could take hours, even days, if nothing changes.
4) Add other sources to vulnerability data. NVD is having long-term problems with funding and organization.

## 💿 Data Models

Simple description/listing of data used and scraped.

### 🐞 CVE

```py
class CVE(BaseModel):
        cve_id: str
        description: str
        published: datetime
        last_modified: datetime
        cvss: CVSS
        cwe_ids: list[int]
```

### 🛡️ CWE

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

### ⚔️ CAPEC

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

### 🩹 Patch

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

### 🛡️ CWEScraper

Scrapes CWE data from the MITRE CWE database.

### ⚔️ CAPECScraper

Scrapes CAPEC data from the MITRE CAPEC database.

### 🐞 CVEScraper

Scrapes CVE data from the NVD database. It requires a patch name, and thus one instance of this scraper is used only to scrape CVEs for one patch.

### 🩹 PatchScraper

Scrapes patch data from the Apple database.

### 🔄 SecurityUpdateScraper

Scrapes patches and their vulnerabilities (CVEs). When scraping CVEs, I must provide a patch name. `CVEScraper` does not scrape all available CVEs like `CWEScraper` does for CWEs. A database of all CVEs would be just too big, and most of the data would not be used. Thus, I combined `PatchScraper` and `CVEScraper` into one scraper that scrapes patches and for every patch scrapes its CVEs.

## ⚒️ Usage

Before running scrapers, download CAPECs and CWEs data. This data will be used by their respective scrapers.

```sh
bash hbit_data/scripts/download_capecs.sh
bash hbit_data/scripts/download_cwes.sh
```

Run scrapers:

```sh
PYTHONPATH=. uv run hbit_data/cli.py scrape_cwes
PYTHONPATH=. uv run hbit_data/cli.py scrape_capecs
PYTHONPATH=. uv run hbit_data/cli.py scrape_patches
PYTHONPATH=. uv run hbit_data/cli.py scrape_security_updates
PYTHONPATH=. uv run hbit_data/cli.py scrape_iphones
```

## ⚙️ Scripts

### 📥 download_capecs.sh

Downloads the latest CAPEC data from MITRE.

### 📥 download_cwes.sh

Downloads the latest CWE data from MITRE.

