import logging
import typing
import xml.etree.ElementTree as ET

from hbit_data import config, dto, utils

from . import base

_log = logging.getLogger(__name__)


class CAPECScraper(base.Scraper[dto.CAPEC]):
    _tag_prefix = "{http://capec.mitre.org/capec-3}"

    def scrape(self) -> typing.Iterator[dto.CAPEC]:
        tree = ET.parse(config.BASE_DIR / "data" / "capecs.xml")
        root = tree.getroot()

        for attack_pattern in root.iter(f"{self._tag_prefix}Attack_Pattern"):
            if not isinstance(attack_pattern, ET.Element):  # type: ignore
                raise ValueError()
            try:
                capec = self._create_capec(attack_pattern)
                yield capec
            except Exception as error:
                id = attack_pattern.get("ID")
                _log.debug("Error parsing CAPEC with ID %s because %s", id, str(error))

    def _create_capec(self, attack_pattern: ET.Element) -> dto.CAPEC:
        capec_id = attack_pattern.get("ID")
        description = attack_pattern.find(f"{self._tag_prefix}Description")
        extended_description = attack_pattern.find(
            f"{self._tag_prefix}Extended_Description"
        )
        likelihood_of_attack = attack_pattern.find(
            f"{self._tag_prefix}Likelihood_Of_Attack"
        )
        severity = attack_pattern.find(f"{self._tag_prefix}Typical_Severity")
        execution_flow = self._create_execution_flow(attack_pattern)
        prerequisites = self._create_prerequisites(attack_pattern)
        skills_required = self._create_skills_required(attack_pattern)
        resources_required = self._create_resources_required(attack_pattern)
        consequences = self._create_consequences(attack_pattern)
        cwe_ids = self._create_cwes(attack_pattern)

        capec = dto.CAPEC(
            capec_id=capec_id,  # type: ignore
            description=utils.get_all_text(description),
            extended_description=utils.get_all_text(extended_description),
            likelihood_of_attack=utils.get_all_text(likelihood_of_attack),
            severity=utils.get_all_text(severity),
            execution_flow=execution_flow,
            prerequisites=prerequisites,
            skills_required=skills_required,
            resources_required=resources_required,
            consequences=consequences,
            cwe_ids=cwe_ids,
        )
        return capec

    def _create_execution_flow(
        self, attack_pattern: ET.Element
    ) -> list[dto.AttackStep]:
        steps_elements = attack_pattern.find(f"{self._tag_prefix}Execution_Flow")
        if steps_elements is None:
            return []

        execution_flow: list[dto.AttackStep] = []
        for step_element in steps_elements.findall(f"{self._tag_prefix}Attack_Step"):
            step = step_element.find(f"{self._tag_prefix}Step")
            description = step_element.find(f"{self._tag_prefix}Description")
            phase = step_element.find(f"{self._tag_prefix}Phase")
            techniques = self._create_techniques(step_element)

            attack_step = dto.AttackStep(
                step=int(utils.get_all_text(step)),
                description=utils.get_all_text(description),
                phase=utils.get_all_text(phase),
                techniques=techniques,
            )
            execution_flow.append(attack_step)

        return execution_flow

    def _create_prerequisites(self, attack_pattern: ET.Element) -> list[str]:
        prerequisites_element = attack_pattern.find(f"{self._tag_prefix}Prerequisites")
        if prerequisites_element is None:
            return []

        all_prerequisit_elements = prerequisites_element.findall(
            f"{self._tag_prefix}Prerequisite"
        )
        prerequisites: list[str] = [
            utils.get_all_text(p) for p in all_prerequisit_elements
        ]

        return prerequisites

    def _create_skills_required(self, attack_pattern: ET.Element) -> list[dto.Skill]:
        skills_elements = attack_pattern.find(f"{self._tag_prefix}Skills_Required")
        if skills_elements is None:
            return []

        skills: list[dto.Skill] = []
        for skill_element in skills_elements.findall(f"{self._tag_prefix}Skill"):
            level = skill_element.get("Level")

            attack_step = dto.Skill(
                level=level,  # type: ignore
                description=utils.get_all_text(skill_element),
            )
            skills.append(attack_step)

        return skills

    def _create_resources_required(self, attack_pattern: ET.Element) -> list[str]:
        resources_element = attack_pattern.find(f"{self._tag_prefix}Resources_Required")
        if resources_element is None:
            return []

        all_resource_elements = resources_element.findall(f"{self._tag_prefix}Resource")
        resources = [utils.get_all_text(r) for r in all_resource_elements]

        return resources

    def _create_consequences(self, attack_pattern: ET.Element) -> list[str]:
        consequences_element = attack_pattern.find(f"{self._tag_prefix}Consequences")
        if consequences_element is None:
            return []

        all_consequence_elements = consequences_element.findall(
            f"{self._tag_prefix}Consequence"
        )
        consequences = [utils.get_all_text(c) for c in all_consequence_elements]

        return consequences

    def _create_techniques(self, attack_step: ET.Element) -> list[str]:
        technique_elements = attack_step.findall(f"{self._tag_prefix}Technique")
        techniques = [utils.get_all_text(te) for te in technique_elements]

        return techniques

    def _create_cwes(self, attack_pattern: ET.Element) -> list[int]:
        weaknesses_elements = attack_pattern.find(
            f"{self._tag_prefix}Related_Weaknesses"
        )
        if weaknesses_elements is None:
            return []

        weaknesses: list[int] = []
        for weakness in weaknesses_elements.findall(
            f"{self._tag_prefix}Related_Weakness"
        ):
            id = weakness.get("CWE_ID")
            if id:
                weaknesses.append(int(id))

        return weaknesses
