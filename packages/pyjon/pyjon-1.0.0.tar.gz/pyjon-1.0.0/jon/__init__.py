r"""
    JON (Just another Object Notation)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    JON is an object notation that allows to declare objects. Here is an example of a JON Document:
    ```
        object = {
            key = value
            key_number = 2
            key_string = "value"
            key_color = rgb { 1 0 0 }
            key_list = { element1 element2 }
            key_dict = {
                subkey = subvalue
            }
        }
    ```

    This module gathers all tools required to parse, create and analyze JON structures.

    :copyright: (c) 2023, Justin Béra (@just1not2) <me@just1not2.org>
    :license: Apache License 2.0 (see LICENSE or https://www.apache.org/licenses/LICENSE-2.0.txt)
"""
__all__ = [
    "BlockStageStatus",
    "get_tokens",
    "JONColor",
    "JONColorType",
    "JONData",
    "JONDict",
    "JONDocument",
    "JONList",
    "JONNumber",
    "JONQuotedString",
    "JONString",
    "JONStringifiedData",
    "JONToken",
    "JONTokenType",
    "JONValidationRule",
    "JONValidationRuleLevel",
    "load",
    "parse",
    "ParsingDecision",
    "ParsingException",
    "ParsingQueue",
    "ParsingRegexKey",
    "PARSING_REGEXES",
    "ParsingStage",
    "ParsingStageConfiguration",
    "ParsingStageKey",
    "ParsingStatus",
    "ParsingValidationError",
    "stage_configuration",
    "validate",
    "VALIDATION_RULES",
]


from jon.datatypes import JONColor, JONColorType, JONData, JONDict, JONDocument, JONList, \
    JONNumber, JONQuotedString, JONString, JONStringifiedData
from jon.main import get_tokens, load, validate
from jon.parsing import parse
from jon.stages import BlockStageStatus, ParsingDecision, ParsingStage, ParsingStageConfiguration, \
    ParsingStageKey, ParsingStatus, stage_configuration
from jon.tokens import JONToken, JONTokenType
from jon.utils import ParsingQueue, ParsingRegexKey, PARSING_REGEXES
from jon.validation import JONValidationRule, JONValidationRuleLevel, ParsingException, \
    ParsingValidationError, VALIDATION_RULES
