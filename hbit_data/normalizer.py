import re
import typing
from functools import total_ordering

import pydantic
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


@total_ordering
class VersionStr:
    def __init__(
        self,
        *,
        major: int,
        minor: int,
        patch: int,
        raw: str,
    ) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.raw = raw

    @property
    def version(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def normalize_version(cls, raw: str) -> "VersionStr":
        try:
            version_reg = (
                r"(?P<major>0|[1-9]\d*)"
                r"(\.(?P<minor>0|[1-9]\d*))?"
                r"(\.(?P<patch>0|[1-9]\d*))?"
            )

            version_reg = re.search(pattern=version_reg, string=raw)
            if not version_reg:
                raise ValueError(
                    f"Version string '{raw}' does not contain "
                    f"any valid version substring."
                )

            version_parts = version_reg.groupdict()
            major = int(version_parts.get("major") or 0)
            minor = int(version_parts.get("minor") or 0)
            patch = int(version_parts.get("patch") or 0)

            return cls(
                major=major,
                minor=minor,
                patch=patch,
                raw=raw,
            )
        except ValueError as value_err:
            raise ValueError(
                f"Incorrect version '{raw}' format. "
                "Supported format: '<digits>.<digits>.<digits>'.",
            ) from value_err
        except (AttributeError, TypeError) as attribute_err:
            raise ValueError(
                f"{raw} is type of '{type(raw)}'. Supported type: string.",
            ) from attribute_err

    @classmethod
    def _pydantic_normalize(cls, input_value: str | typing.Self) -> "VersionStr":
        if isinstance(input_value, str):
            return cls.normalize_version(input_value)
        else:
            return input_value

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source: type[typing.Any],
        _handler: pydantic.GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._pydantic_normalize,
            core_schema.json_or_python_schema(
                json_schema=core_schema.str_schema(),
                python_schema=core_schema.union_schema(
                    [
                        core_schema.is_instance_schema(cls),
                        core_schema.str_schema(),
                    ],
                ),
                serialization=core_schema.to_string_ser_schema(),
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: core_schema.CoreSchema,
        handler: pydantic.GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        field_schema = handler(core_schema)
        field_schema.update(type="str")
        return field_schema

    def __eq__(self, other: typing.Any) -> bool:
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )

    def __lt__(self, other: typing.Any) -> bool:
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __le__(self, other: typing.Any) -> bool:
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.major, self.minor, self.patch) <= (
            other.major,
            other.minor,
            other.patch,
        )

    def _is_valid_operand(self, other: typing.Any) -> bool:
        return (
            hasattr(other, "major")
            and hasattr(other, "minor")
            and hasattr(other, "patch")
        )

    def __str__(self) -> str:
        return self.version

    def __repr__(self) -> str:
        return f"Version({self.version})"

    def __hash__(self) -> int:
        return hash(self.version)


Version = pydantic.TypeAdapter(VersionStr)
