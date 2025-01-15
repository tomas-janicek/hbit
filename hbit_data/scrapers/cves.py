import logging
import typing

from common import requests
from hbit_data import dto, normalizer

from . import base

_log = logging.getLogger(__name__)


class CVEScraper(base.Scraper[dto.CVE]):
    def __init__(self, request: requests.Requests, patch_name: str) -> None:
        self.patch_name = patch_name
        self.request = request
        self.nvd_base = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    def scrape(self) -> typing.Iterator[dto.CVE]:
        params = self._create_nvd_params()

        data = self.request.get_or_retry(
            base=self.nvd_base,
            path="",
            response_type=dict[str, typing.Any],
            params=params,
            timeout=60,
        )
        if not data:
            raise Exception(
                f"Error loading CVEs data for patch {self.patch_name} from {self.nvd_base}."
            )

        vulnerabilities = data.get("vulnerabilities", [])
        for vul in vulnerabilities:
            try:
                cve = self._create_cve(vul)
            except Exception as error:
                _log.warning("Error scraping CVE because %s", str(error))
                continue

            yield cve

    def _create_nvd_params(self) -> dict[str, str]:
        # TODO: Write why we need to increase original patch
        # TODO: Why isn't this taken care of by excluding?
        incremented_patch = normalizer.Version.validate_python(self.patch_name)
        incremented_patch.patch += 1
        params = {
            "virtualMatchString": "cpe:2.3:o:apple:iphone_os",
            "versionStart": incremented_patch.version,
            "versionStartType": "excluding",
        }

        return params

    def _create_cve(self, vul: dict[str, typing.Any]) -> dto.CVE:
        cve_detail: dict[str, typing.Any] = vul["cve"]
        description = self._create_description(cve_detail.get("descriptions"))
        cvss = self._create_cvss(cve_detail.get("metrics"))
        cwe_ids = self._create_cwe_ids(cve_detail.get("weaknesses"))

        cve = dto.CVE(
            cve_id=cve_detail.get("id"),  # type: ignore
            description=description,
            published=cve_detail.get("published"),  # type: ignore
            last_modified=cve_detail.get("lastModified"),  # type: ignore
            cvss=cvss,
            cwe_ids=cwe_ids,
        )

        return cve

    def _create_description(
        self, descriptions: list[dict[str, typing.Any]] | None
    ) -> str:
        if not descriptions:
            raise ValueError(
                f"CVE scraped for patch {self.patch_name} is missing descriptions."
            )

        for description in descriptions:
            if description.get("lang") != "en":
                continue

            text = description.get("value")
            if text:
                return text

        raise ValueError(
            f"CVE scraped for patch {self.patch_name} does not have english translation."
        )

    def _create_cvss(self, metrics: dict[str, typing.Any] | None) -> dto.CVSS:
        if not metrics:
            raise ValueError(
                f"CVSS scraped for patch {self.patch_name} is missing CVSS info."
            )

        cvss_v31 = metrics.get("cvssMetricV31")
        if not cvss_v31:
            raise ValueError(
                f"CVSS scraped for patch {self.patch_name} is missing CVSS v3 info."
            )

        for cvss_entry in cvss_v31:
            if not cvss_entry.get("type").lower() != "Primary":
                continue

            cvss_data = cvss_entry.get("cvssData")
            cvss = dto.CVSS(
                version=cvss_data.get("version"),
                vector=cvss_data.get("vectorString"),
                score=cvss_data.get("baseScore"),
                exploitability_score=cvss_entry.get("exploitabilityScore"),
                impact_score=cvss_entry.get("impactScore"),
            )
            return cvss

        raise ValueError(
            f"CVSS scraped for patch {self.patch_name} does not have primary entry."
        )

    def _create_cwe_ids(
        self, weaknesses: list[dict[str, typing.Any]] | None
    ) -> list[int]:
        if not weaknesses:
            raise ValueError(
                f"CVE scraped for patch {self.patch_name} is missing CWE info."
            )
        cwe_ids: set[int] = set()
        for weakness in weaknesses:
            weakness_descriptions = weakness.get("description")
            if not weakness_descriptions:
                raise ValueError(
                    f"CWE craped for patch {self.patch_name} does not have description."
                )

            for description in weakness_descriptions:
                cwe_id = description.get("value")
                if cwe_id:
                    if not (cwe := self._validate_cwe(cwe_id)):
                        continue

                    cwe_ids.add(cwe)

        return list(cwe_ids)

    def _validate_cwe(self, raw: str | None) -> int | None:
        # immediately return if none
        if not raw:
            return None
        cve_normalized = raw.strip().lower()
        # make sure it is standard CWE in form "CWE-*", not something like "NVD-CWE-Other"
        if not "cwe-" == cve_normalized[:4]:
            return None
        try:
            cwe_int = int(cve_normalized.replace("cwe-", ""))
            return cwe_int
        except Exception:
            _log.warning("CWE %s could not be parsed.", raw)
            return None
