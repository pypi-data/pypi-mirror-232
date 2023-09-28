r"""
    jon.validation
    ~~~~~~~~~~~~~~

    Validation rules and errors for JON parsing

    :copyright: (c) 2023, Justin Béra (@just1not2) <me@just1not2.org>
    :license: Apache License 2.0 (see LICENSE or https://www.apache.org/licenses/LICENSE-2.0.txt
"""
__all__ = [
    "JONValidationRule",
    "JONValidationRuleLevel",
    "ParsingException",
    "ParsingValidationError",
    "VALIDATION_RULES",
]

from enum import Enum
from typing import Tuple


class JONValidationRuleLevel(Enum):
    """Validation rule level class"""

    ERROR = 0
    WARNING = 1
    UNKNOWN = 2


class JONValidationRule:
    """Validation rules class for JON documents"""

    def __init__(self, key: str, name: str, description: str) -> None:
        self.key = key
        self.name = name
        self.description = description

        if self.key != "" and self.key[0] == "E":
            self.level = JONValidationRuleLevel.ERROR
        elif self.key != "" and self.key[0] == "W":
            self.level = JONValidationRuleLevel.WARNING
        else:
            self.level = JONValidationRuleLevel.UNKNOWN


VALIDATION_RULES = {
    "E001": JONValidationRule(
        key="E001",
        name="unexpected-eol",
        description="Unexpected end of line",
    ),
    "E002": JONValidationRule(
        key="E002",
        name="unexpected-char",
        description="Unexpected character",
    ),
    "E003": JONValidationRule(
        key="E003",
        name="unclosed-block",
        description="Unclosed block",
    ),
    "W001": JONValidationRule(
        key="W001",
        name="indent-mix-tabs-spaces",
        description="Inconsistent use of tab(s) and space(s) for indent",
    ),
    "W002": JONValidationRule(
        key="W002",
        name="trailing-whitespaces",
        description="Trailing whitespace(s) at the end of the line",
    ),
    "W003": JONValidationRule(
        key="W003",
        name="indent-whitespaces",
        description="Incorrect number of whitespaces for indent",
    ),
    "W004": JONValidationRule(
        key="W004",
        name="separating-space",
        description="Separation of exactly one whitespace not respected",
    ),
    "W005": JONValidationRule(
        key="W005",
        name="separating-tabs",
        description="Use of tabs outside of indent context",
    ),
}


class ParsingValidationError:
    """Parsing validation error class"""

    def __init__(
        self,
        rule_key: JONValidationRule,
        positions: Tuple[Tuple[int, int], Tuple[int, int]],
    ):
        self.rule = VALIDATION_RULES[rule_key]
        self.positions = positions

    def stringify(self):
        """Return a stringified version of the validation error"""

        return (
            f"({self.positions[0][0]}:{self.positions[0][1]})->({self.positions[1][0]}:" +
            f"{self.positions[1][1]}): {self.rule.key}: {self.rule.description} ({self.rule.name})"
        )


class ParsingException(Exception):
    """Exception class for parsing validation errors"""

    def __init__(self, error: ParsingValidationError):
        self.error = error
        super().__init__(
            f"The parser encountered the following validation error: '{error.stringify()}'"
        )
