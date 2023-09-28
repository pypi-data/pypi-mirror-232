r"""
    jon.parsing
    ~~~~~~~~~~~

    JON parsing function

    :copyright: (c) 2023, Justin Béra (@just1not2) <me@just1not2.org>
    :license: Apache License 2.0 (see LICENSE or https://www.apache.org/licenses/LICENSE-2.0.txt
"""
__all__ = [
    "parse",
]

from typing import List, Tuple
from .datatypes import JONDocument
from .stages import BlockStageStatus, ParsingStage, ParsingStageKey
from .tokens import JONToken
from .utils import ParsingQueue
from .validation import ParsingValidationError


def parse(source: str) -> Tuple[JONDocument, List[ParsingValidationError], List[JONToken]]:
    """Parse a JON-formatted string"""

    queue = ParsingQueue(source)
    validation_errors: List[ParsingValidationError] = []
    tokens: List[JONToken] = []
    document = JONDocument()

    root_stage = ParsingStage(
        queue=queue,
        validation_errors=validation_errors,
        tokens=tokens,
        config_key=ParsingStageKey.BLOCK_DICT,
        data=document,
        block_stage_status=BlockStageStatus.DICT,
    )
    root_stage.next()

    return document, validation_errors, tokens
