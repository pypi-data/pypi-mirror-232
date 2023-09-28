r"""
    jon.main
    ~~~~~~~~

    JON main functions

    :copyright: (c) 2023, Justin Béra (@just1not2) <me@just1not2.org>
    :license: Apache License 2.0 (see LICENSE or https://www.apache.org/licenses/LICENSE-2.0.txt
"""
__all__ = [
    "get_tokens",
    "load",
    "validate",
]

from typing import List
from jon.datatypes import JONDocument
from jon.parsing import parse
from jon.tokens import JONToken
from jon.validation import JONValidationRuleLevel, ParsingException, ParsingValidationError


def load(source: str) -> JONDocument:
    """Load a JON-formatted string"""

    document, validation_errors, _ = parse(source=source)

    for error in validation_errors:
        if error.rule.level == JONValidationRuleLevel.ERROR:
            raise ParsingException(error=error)

    return document


def validate(source: str) -> List[ParsingValidationError]:
    """Validate a JON-formatted string"""

    _, validation_errors, _ = parse(source=source)
    return validation_errors


def get_tokens(source: str) -> List[JONToken]:
    """Get an ordered list of semantic tokens of a JON-formatted string"""

    _, _, tokens = parse(source=source)
    return tokens
