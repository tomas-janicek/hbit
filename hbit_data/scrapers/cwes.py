import logging
import typing
import xml.etree.ElementTree as ET

from hbit_data import config, dto, utils

from . import base

_log = logging.getLogger(__name__)


class CWEScraper(base.Scraper[dto.CWE]):
    _tag_prefix = "{http://cwe.mitre.org/cwe-7}"

    def scrape(self) -> typing.Iterator[dto.CWE]:
        tree = ET.parse(config.BASE_DIR / "data" / "cwes.xml")
        root = tree.getroot()

        for weakness in root.iter(f"{self._tag_prefix}Weakness"):
            if not isinstance(weakness, ET.Element):  # type: ignore
                raise ValueError()
            try:
                cwe = self._create_cwe(weakness)
                yield cwe
            except Exception as error:
                id = weakness.get("ID")
                _log.debug("Error parsing CWE with ID %s because %s", id, str(error))

    def _create_cwe(self, weakness: ET.Element) -> dto.CWE:
        cwe_id = weakness.get("ID")
        name = weakness.get("Name")
        description = weakness.find(f"{self._tag_prefix}Description")
        extended_description = weakness.find(f"{self._tag_prefix}Extended_Description")
        likelihood_of_exploit = weakness.find(
            f"{self._tag_prefix}Likelihood_Of_Exploit"
        )
        background_details = self._create_bg_details(weakness)
        potential_mitigations = self._create_mitigations(weakness)
        detection_methods = self._create_detection_methods(weakness)

        cwe = dto.CWE(
            cwe_id=cwe_id,  # type: ignore
            name=name,  # type: ignore
            description=utils.get_all_text(description),
            extended_description=utils.get_all_text(extended_description),
            likelihood_of_exploit=utils.get_all_text(likelihood_of_exploit),
            background_details=background_details,
            potential_mitigations=potential_mitigations,
            detection_methods=detection_methods,
        )

        return cwe

    def _create_bg_details(self, weakness: ET.Element) -> list[str]:
        bg_details_element = weakness.find(f"{self._tag_prefix}Background_Details")
        if bg_details_element is None:
            return []

        all_bg_details = bg_details_element.findall(
            f"{self._tag_prefix}Background_Detail"
        )
        bg_details = [utils.get_all_text(bg) for bg in all_bg_details]

        return bg_details

    def _create_mitigations(self, weakness: ET.Element) -> list[dto.Mitigation]:
        mitigations_elements = weakness.find(f"{self._tag_prefix}Potential_Mitigations")
        if mitigations_elements is None:
            return []
        mitigations: list[dto.Mitigation] = []
        for mitigation_element in mitigations_elements.findall(
            f"{self._tag_prefix}Mitigation"
        ):
            description = mitigation_element.find(f"{self._tag_prefix}Description")
            effectiveness = mitigation_element.find(f"{self._tag_prefix}Effectiveness")
            effectiveness_notes = mitigation_element.find(
                f"{self._tag_prefix}Effectiveness_Notes"
            )

            mitigation = dto.Mitigation(
                description=utils.get_all_text(description),
                effectiveness=utils.get_all_text(effectiveness),
                effectiveness_notes=utils.get_all_text(effectiveness_notes),
            )
            mitigations.append(mitigation)

        return mitigations

    def _create_detection_methods(
        self, weakness: ET.Element
    ) -> list[dto.DetectionMethod]:
        methods_elements = weakness.find(f"{self._tag_prefix}Detection_Methods")
        if methods_elements is None:
            return []
        methods: list[dto.DetectionMethod] = []
        for method_element in methods_elements.findall(
            f"{self._tag_prefix}Detection_Method"
        ):
            method = method_element.find(f"{self._tag_prefix}Method")
            description = method_element.find(f"{self._tag_prefix}Description")
            effectiveness = method_element.find(f"{self._tag_prefix}Effectiveness")

            method = dto.DetectionMethod(
                method=utils.get_all_text(method),
                description=utils.get_all_text(description),
                effectiveness=utils.get_all_text(effectiveness),
            )
            methods.append(method)

        return methods
