import typing

from common import requests
from hbit_data import dto

from . import base, cves, patches


class SecurityUpdateScraper(base.Scraper[dto.SecurityUpdate]):
    def __init__(self, request: requests.Requests) -> None:
        self.request = request

    def scrape(self) -> typing.Iterator[dto.SecurityUpdate]:
        patch_scraper = patches.PatchScraper(self.request)
        scraped_patches = patch_scraper.scrape()

        for patch in scraped_patches:
            cve_scraper = cves.CVEScraper(self.request, patch.name)
            scraped_cves = cve_scraper.scrape()
            security_updates = dto.SecurityUpdate(
                patch=patch,
                cves=list(scraped_cves),
            )
            yield security_updates
