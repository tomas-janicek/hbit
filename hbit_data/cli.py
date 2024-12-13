import httpx
import typer

from hbit_data import (
    clients,
    dto,
    pipelines,
    processors,
    requests,
    settings,
)
from hbit_data.scrapers import capecs, cwes, patches, security_updates

cli = typer.Typer()


@cli.command(name="scrape_security_updates")
def scrape_security_updates() -> None:
    hbit_request = requests.HTTPXRequests(requests.create_hbit_api_client())
    hbit = clients.HBITClient(request=hbit_request, hbit_api_url=settings.HBIT_API_URL)
    processor = processors.ItemProcessor[dto.SecurityUpdate](
        batch_size=2,
        pipelines=[
            pipelines.JSONDumpPipeline[dto.SecurityUpdate]("scraped_updates.json"),
            pipelines.SecurityUpdatesHBITPipeline(hbit),
        ],
    )

    request = requests.HTTPXRequests(httpx.Client())
    update_scraper = security_updates.SecurityUpdateScraper(request)
    processor.process(update_scraper)


@cli.command(name="scrape_cwes")
def scrape_cwes() -> None:
    hbit_request = requests.HTTPXRequests(requests.create_hbit_api_client())
    hbit = clients.HBITClient(request=hbit_request, hbit_api_url=settings.HBIT_API_URL)
    processor = processors.ItemProcessor[dto.CWE](
        batch_size=32,
        pipelines=[
            pipelines.JSONDumpPipeline[dto.CWE]("scraped_cwes.json"),
            pipelines.CWEHBITPipeline(hbit),
        ],
    )

    cwe_scraper = cwes.CWEScraper()
    processor.process(cwe_scraper)


@cli.command(name="scrape_capecs")
def scrape_capecs() -> None:
    hbit_request = requests.HTTPXRequests(requests.create_hbit_api_client())
    hbit = clients.HBITClient(request=hbit_request, hbit_api_url=settings.HBIT_API_URL)
    processor = processors.ItemProcessor[dto.CAPEC](
        batch_size=32,
        pipelines=[
            pipelines.JSONDumpPipeline[dto.CAPEC]("scraped_capecs.json"),
            pipelines.CAPECHBITPipeline(hbit),
        ],
    )

    capec_scraper = capecs.CAPECScraper()
    processor.process(capec_scraper)


@cli.command(name="scrape_patches")
def scrape_patches() -> None:
    hbit_request = requests.HTTPXRequests(requests.create_hbit_api_client())
    hbit = clients.HBITClient(request=hbit_request, hbit_api_url=settings.HBIT_API_URL)
    processor = processors.ItemProcessor[dto.Patch](
        batch_size=32,
        pipelines=[
            pipelines.JSONDumpPipeline[dto.Patch]("scraped_patches.json"),
            pipelines.PatchesHBITPipeline(hbit),
        ],
    )

    request = requests.HTTPXRequests(httpx.Client())
    patch_scraper = patches.PatchScraper(request)
    processor.process(patch_scraper)


if __name__ == "__main__":
    cli()
