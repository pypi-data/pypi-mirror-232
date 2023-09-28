r"""
    jon.tokens
    ~~~~~~~~~~

    JON semantic tokens definition

    :copyright: (c) 2023, Justin Béra (@just1not2) <me@just1not2.org>
    :license: Apache License 2.0 (see LICENSE or https://www.apache.org/licenses/LICENSE-2.0.txt
"""
__all__ = [
    "JONToken",
    "JONTokenType",
]

from enum import Enum
from typing import Tuple


class JONTokenType(Enum):
    """Possible types of JON tokens"""

    STRING = "STRING"
    NUMBER = "NUMBER"
    QUOTED_STRING = "QUOTED_STRING"
    COMMENT = "COMMENT"
    FUNCTION = "FUNCTION"


class JONToken:
    """Semantic token class for JON-formatted documents"""

    def __init__(
        self,
        positions: Tuple[Tuple[int, int], Tuple[int, int]],
        token_type: JONTokenType,
    ):
        self.positions = positions
        self.token_type = token_type

    def stringify(self):
        """Return a stringified version of the token"""

        return (
            f"({self.positions[0][0]}:{self.positions[0][1]})->" +
            f"({self.positions[1][0]}:{self.positions[1][1]}): {self.token_type.value}"
        )
