r"""
    jon.utils
    ~~~~~~~~~

    Basic utility functions

    :copyright: (c) 2023, Justin Béra (@just1not2) <me@just1not2.org>
    :license: Apache License 2.0 (see LICENSE or https://www.apache.org/licenses/LICENSE-2.0.txt
"""
__all__ = [
    "ParsingQueue",
    "PARSING_REGEXES",
    "ParsingRegexKey",
]

import re
from enum import Enum
from typing import Optional, Tuple


class ParsingQueue:
    """Parsing queue class"""

    def __init__(self, source: str) -> None:
        self.content = source
        self.line = 1
        self.column = 0
        self.last_line = self.line
        self.last_column = self.column - 1
        self.saved_line = -1
        self.saved_column = -1
        self._save: Optional[ParsingQueue] = None

    def next(self) -> Optional[str]:
        """Get the next character in queue"""

        # Save last position
        self.last_line = self.line
        self.last_column = self.column

        if self.content == "":
            return None

        char = self.content[0]
        self.content = self.content[1:]

        if char == "\n":
            self.column = 0
            self.line += 1
        else: self.column += 1

        return char

    def save_position(self) -> None:
        """Save the current position"""

        self.saved_line = self.line
        self.saved_column = self.column

    def save(self) -> None:
        """
        Save the state of the queue
        """

        self._save = ParsingQueue("")
        self._save.content = self.content
        self._save.line = self.line
        self._save.column = self.column
        self._save.last_line = self.last_line
        self._save.last_column = self.last_column
        self._save.saved_line = self.saved_line
        self._save.saved_column = self.saved_column

    def restore(self) -> None:
        """Restore the queue from its save"""

        if self._save is not None:
            self.content = self._save.content
            self.line = self._save.line
            self.column = self._save.column
            self.last_line = self._save.last_line
            self.last_column = self._save.last_column
            self.saved_line = self._save.saved_line
            self.saved_column = self._save.saved_column

    def get_position(self) -> Tuple[int, int]:
        """Return the current position"""

        return (self.line, self.column)

    def get_positions(self, exclude_last=False) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Return the saved and current position. This method can interfere with the put_back method
        """

        saved_position = (self.saved_line, self.saved_column)
        if exclude_last:
            return (saved_position, (self.last_line, self.last_column))
        return (saved_position, (self.line, self.column))

    def go_to_new_line(self):
        """Advance in the queue until a newline char is matched"""

        char = ""
        while char is not None and char != "\n":
            char = self.next()
        return char


class ParsingRegexKey(Enum):
    """Parsing regexes enumeration"""

    WORD = "WORD"
    LETTER = "LETTER"
    NUMBER = "NUMBER"
    DECIMAL_NUMBER = "DECIMAL_NUMBER"
    QUOTE = "QUOTE"
    NO_QUOTE = "NO_QUOTE"
    NO_WHITESPACE = "NO_WHITESPACE"
    ASSIGN = "ASSIGN"
    NEWLINE = "NEWLINE"
    OPEN_BRACE = "OPEN_BRACE"
    CLOSE_BRACE = "CLOSE_BRACE"
    HASHTAG = "HASHTAG"
    NEVER = "NEVER"


PARSING_REGEXES = {
    ParsingRegexKey.WORD: re.compile("[\\w:\\.\\/-]"),
    ParsingRegexKey.LETTER: re.compile("[a-zA-Z@]"),
    ParsingRegexKey.NUMBER: re.compile("[\\d-]"),
    ParsingRegexKey.DECIMAL_NUMBER: re.compile("[\\d\\.]"),
    ParsingRegexKey.QUOTE: re.compile("\""),
    ParsingRegexKey.NO_QUOTE: re.compile("[^\\n\"]"),
    ParsingRegexKey.NO_WHITESPACE: re.compile("[^\\n\\t ]"),
    ParsingRegexKey.ASSIGN: re.compile("="),
    ParsingRegexKey.NEWLINE: re.compile("\\n"),
    ParsingRegexKey.OPEN_BRACE: re.compile("{"),
    ParsingRegexKey.CLOSE_BRACE: re.compile("}"),
    ParsingRegexKey.HASHTAG: re.compile("#"),
    ParsingRegexKey.NEVER: re.compile(" ^"),
}
