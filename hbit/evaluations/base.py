import logging
import typing

from common import dto as common_dto

_log = logging.getLogger(__name__)


class DeviceEvaluationService(typing.Protocol):
    def get_full_evaluation(
        self, device_identifier: str, patch_build: str
    ) -> common_dto.DeviceEvaluationDto: ...

    def get_trimmed_evaluation(
        self, device_identifier: str, patch_build: str
    ) -> common_dto.DeviceEvaluationDto: ...


class PatchEvaluationService(typing.Protocol):
    def get_full_evaluation(
        self, patch_build: str
    ) -> common_dto.PatchEvaluationDto: ...

    def get_trimmed_evaluation(
        self, patch_build: str
    ) -> common_dto.PatchEvaluationDto: ...
