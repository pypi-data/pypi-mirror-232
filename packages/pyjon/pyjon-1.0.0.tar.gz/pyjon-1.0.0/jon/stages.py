r"""
    jon.stages
    ~~~~~~~~~~

    JON parsing stages definition and execution

    :copyright: (c) 2023, Justin Béra (@just1not2) <me@just1not2.org>
    :license: Apache License 2.0 (see LICENSE or https://www.apache.org/licenses/LICENSE-2.0.txt
"""
from __future__ import annotations
__all__ = [
    "BlockStageStatus",
    "ParsingDecision",
    "ParsingStage",
    "ParsingStageConfiguration",
    "ParsingStageKey",
    "ParsingStatus",
    "stage_configuration",
]

from enum import Enum
from typing import Callable, List, Optional, Tuple
from .datatypes import JONColor, JONColorType, JONData, JONDict, JONList, JONNumber, \
    JONQuotedString, JONString
from .tokens import JONToken, JONTokenType
from .utils import ParsingQueue, PARSING_REGEXES, ParsingRegexKey
from .validation import ParsingValidationError


class ParsingStatus(Enum):
    """Possible outcomes after parsing a stage"""

    # The parent stage must continue with next stage
    CONTINUE = 0

    # Current stage must continue with next stage
    ENTER = 1

    # The parent stage must stop and restart its stage
    QUIT = 2

    # The parent stage must stop and its parent must restart its stage
    SUPERQUIT = 3


class ParsingStageKey(Enum):
    """Possible keys that define a stage"""

    # Abstract stage that creates list or unknown blocks
    BLOCK_LIST = "BLOCK_LIST"

    # Abstract stage that creates dict blocks
    BLOCK_DICT = "BLOCK_DICT"

    # Abstract stage that creates color blocks
    BLOCK_COLOR = "BLOCK_COLOR"

    # Stage that defines indent at the beginning of a line of a list
    INDENT_LIST = "INDENT_LIST"

    # Stage that defines indent at the beginning of a line of a dict
    INDENT_DICT = "INDENT_DICT"

    # Stage that defines a string key
    KEY_STRING = "KEY_STRING"

    # Stage that defines a number key
    KEY_NUMBER = "KEY_NUMBER"

    # Stage that defines a quoted string key
    KEY_QUOTED_STRING = "KEY_QUOTED_STRING"

    # Stage that defines the end of a quoted string key
    END_KEY_QUOTED_STRING = "END_KEY_QUOTED_STRING"

    # Stage that defines the assignment of a key to its value
    ASSIGNMENT = "ASSIGNMENT"

    # Stage that defines a string value
    VALUE_STRING = "VALUE_STRING"

    # Stage that defines a number value
    VALUE_NUMBER = "VALUE_NUMBER"

    # Stage that defines a quoted string value
    VALUE_QUOTED_STRING = "VALUE_QUOTED_STRING"

    # Stage that defines the end of a quoted string value
    END_VALUE_QUOTED_STRING = "END_VALUE_QUOTED_STRING"

    # Stage that defines a block value
    VALUE_BLOCK = "VALUE_BLOCK"

    # Stage that defines the end of a block
    END_BLOCK = "END_BLOCK"

    # Stage that defines a comment
    COMMENT = "COMMENT"

    # Stage that defines a comment after the beginning of a block
    COMMENT_START_BLOCK = "COMMENT_START_BLOCK"

    # Stage that defines a comment after the end of a block
    COMMENT_END_BLOCK = "COMMENT_END_BLOCK"


class ParsingStageConfiguration:
    """Configuration of possible stages"""

    def __init__(
            self,
            regex: ParsingRegexKey = ParsingRegexKey.NEVER,
            decisions: Optional[List[ParsingDecision]] = None,
            data_type: Optional[JONData] = None,
            data_key = False,
            force_enter_in: Optional[ParsingStageKey] = None,
            has_indent = False,
            can_be_last_at_depth: Optional[int] = None,
            token_type: Optional[JONTokenType] = None,
            include_last_in_token = False,
        ) -> None:

        # Regex that allows to stay in the stage
        self.regex = regex

        # Decisions to consider for the next stage
        if decisions is not None:
            self.decisions = decisions
        else:
            self.decisions = []

        # Type of the data of the stage
        # None means the stage does not hold data
        self.data_type = data_type

        # Determine if the data should be saved as a key
        self.data_key = data_key

        # Force the stage to enter to the stage with this configuration key without parsing
        # This overwrites regex and decisions
        self.force_enter_in = force_enter_in

        # Set the indent rules for the whitespaces count of this stage:
        # - tabs are allowed to replace spaces and are worth 4 spaces each
        # - expected_whitespaces_count = 4 * (self.depth - (1 if char == '}' else 0))
        self.has_indent = has_indent

        # Allow the stage with a specific depth to end parsing when the queue is empty
        self.can_be_last_at_depth = can_be_last_at_depth

        # Type of tokens to attribute to chars that are matched in the stage
        self.token_type = token_type

        # Include next character in the token
        self.include_last_in_token = include_last_in_token


class ParsingDecision:
    """Decisions to consider for a parsing stage"""

    def __init__(
        self,
        regex: ParsingRegexKey = ParsingRegexKey.NEVER,
        status: ParsingStatus = ParsingStatus.CONTINUE,
        default = False,
        key: Optional[ParsingStageKey] = None,
        pass_matched_char = False,
        skip_whitespaces_count = False,
        update_parent_block_stage_status: Optional[BlockStageStatus] = None,
        inline = False,
        if_data_function: Optional[Callable[[JONData], bool]] = None,
        replace_data_pass_function: Optional[Callable[[JONData], Tuple[
            JONData,
            JONTokenType,
            BlockStageStatus
        ]]] = None,
    ) -> None:
        # Regex to match to choose this decision
        self.regex = regex

        # Parsing status of this decision
        self.status = status

        # Make this decision the default decision
        # A default decision should appear at the end of the decision list
        # In a default decision, the queue is restored from the start of space separation and
        # whitespace count is skipped
        self.default = default

        # Key of the destination stage of this decision
        # This is only useful for CONTINUE and ENTER statuses
        self.key = key

        # Initialize next stage data content with the matched character
        self.pass_matched_char = pass_matched_char

        # Do not check the number of whitespaces for this decision
        self.skip_whitespaces_count = skip_whitespaces_count

        # Update the parent block stage status
        self.update_parent_block_stage_status = update_parent_block_stage_status

        # Initialize next stage as inline
        self.inline = inline

        # Function that check if the data allows this decision
        self.if_data_function = if_data_function

        # Function that replaces the data of current stage and pass it to next stage
        # First return value is the new data to replace the old one
        # Second return value is the token to replace the old one
        # Third parameter is the Block Stage Status for the next stage
        self.replace_data_pass_function = replace_data_pass_function


class BlockStageStatus(Enum):
    """Possible types of block stages"""

    UNKNOWN = 0
    LIST = 1
    DICT = 2
    COLOR = 3


def stage_configuration(key, parent_stage: Optional[ParsingStage]) -> ParsingStageConfiguration:
    """Get a stage configuration given a parent stage"""

    if key == ParsingStageKey.BLOCK_LIST:
        return ParsingStageConfiguration(
            data_type=JONList,
            force_enter_in=ParsingStageKey.INDENT_LIST,
        )

    if key == ParsingStageKey.BLOCK_DICT:
        return ParsingStageConfiguration(
            data_type=JONDict,
            force_enter_in=ParsingStageKey.INDENT_DICT,
        )

    if key == ParsingStageKey.BLOCK_COLOR:
        return ParsingStageConfiguration(
            data_type=JONColor,
            force_enter_in=ParsingStageKey.INDENT_LIST,
        )

    if key == ParsingStageKey.INDENT_LIST:
        non_inline_decisions = [
            ParsingDecision(regex=ParsingRegexKey.NEWLINE, status=ParsingStatus.QUIT),
            ParsingDecision(regex=ParsingRegexKey.HASHTAG, key=ParsingStageKey.COMMENT),
        ] if not parent_stage.inline else []

        closing_brace_decision = []
        general_decisions = []

        # Color blocks can only contain exactly 3 JONNumbers
        if parent_stage is not None and parent_stage.block_stage_status == BlockStageStatus.COLOR:
            general_decisions = [
                ParsingDecision(
                    regex=ParsingRegexKey.CLOSE_BRACE,
                    key=ParsingStageKey.END_BLOCK,
                ),
            ] if parent_stage.data.is_full() else [
                ParsingDecision(
                    regex=ParsingRegexKey.NUMBER,
                    key=ParsingStageKey.VALUE_NUMBER,
                    pass_matched_char=True,
                ),
            ]
        else:
            # A block can only be closed if that corresponds to an opening brace
            closing_brace_decision = [
                ParsingDecision(
                    regex=ParsingRegexKey.CLOSE_BRACE,
                    key=ParsingStageKey.END_BLOCK,
                ),
            ] if parent_stage is not None and parent_stage.depth != -1 else []

            general_decisions = [
                ParsingDecision(
                    regex=ParsingRegexKey.LETTER,
                    key=ParsingStageKey.VALUE_STRING,
                    pass_matched_char=True,
                ),
                ParsingDecision(
                    regex=ParsingRegexKey.NUMBER,
                    key=ParsingStageKey.VALUE_NUMBER,
                    pass_matched_char=True,
                ),
                ParsingDecision(
                    regex=ParsingRegexKey.QUOTE,
                    key=ParsingStageKey.VALUE_QUOTED_STRING,
                ),
                ParsingDecision(
                    regex=ParsingRegexKey.OPEN_BRACE,
                    key=ParsingStageKey.VALUE_BLOCK,
                    update_parent_block_stage_status=BlockStageStatus.LIST,
                ),
            ]

        return ParsingStageConfiguration(
            decisions=general_decisions + closing_brace_decision + non_inline_decisions,
            has_indent=(not parent_stage.inline),
            can_be_last_at_depth=0,
        )

    if key == ParsingStageKey.INDENT_DICT:
        # A block can only be closed if that corresponds to an opening brace
        closing_brace_decision = [
            ParsingDecision(
                regex=ParsingRegexKey.CLOSE_BRACE,
                key=ParsingStageKey.END_BLOCK,
            ),
        ] if parent_stage is not None and parent_stage.depth != -1 else []

        non_inline_decisions = [
            ParsingDecision(regex=ParsingRegexKey.NEWLINE, status=ParsingStatus.QUIT),
            ParsingDecision(regex=ParsingRegexKey.HASHTAG, key=ParsingStageKey.COMMENT),
        ] if not parent_stage.inline else []

        return ParsingStageConfiguration(
            decisions=[
                ParsingDecision(
                    regex=ParsingRegexKey.LETTER,
                    key=ParsingStageKey.KEY_STRING,
                    pass_matched_char=True,
                ),
                ParsingDecision(
                    regex=ParsingRegexKey.NUMBER,
                    key=ParsingStageKey.KEY_NUMBER,
                    pass_matched_char=True,
                ),
                ParsingDecision(
                    regex=ParsingRegexKey.QUOTE,
                    key=ParsingStageKey.KEY_QUOTED_STRING,
                ),
            ] + closing_brace_decision + non_inline_decisions,
            has_indent=(not parent_stage.inline),
            can_be_last_at_depth=0,
        )

    if key == ParsingStageKey.KEY_STRING:
        return ParsingStageConfiguration(
            regex=ParsingRegexKey.WORD,
            decisions=[
                ParsingDecision(regex=ParsingRegexKey.ASSIGN, key=ParsingStageKey.ASSIGNMENT),
            ],
            data_type=JONString,
            data_key=True,
            token_type=JONTokenType.STRING,
        )

    if key == ParsingStageKey.KEY_NUMBER:
        return ParsingStageConfiguration(
            regex=ParsingRegexKey.DECIMAL_NUMBER,
            decisions=[
                ParsingDecision(regex=ParsingRegexKey.ASSIGN, key=ParsingStageKey.ASSIGNMENT),
            ],
            data_type=JONNumber,
            data_key=True,
            token_type=JONTokenType.NUMBER,
        )

    if key == ParsingStageKey.KEY_QUOTED_STRING:
        return ParsingStageConfiguration(
            regex=ParsingRegexKey.NO_QUOTE,
            decisions=[
                ParsingDecision(
                    regex=ParsingRegexKey.QUOTE,
                    key=ParsingStageKey.END_KEY_QUOTED_STRING,
                    skip_whitespaces_count=True,
                ),
            ],
            data_type=JONQuotedString,
            data_key=True,
            token_type=JONTokenType.QUOTED_STRING,
            include_last_in_token=True,
        )

    if key == ParsingStageKey.END_KEY_QUOTED_STRING:
        return ParsingStageConfiguration(
            decisions=[
                ParsingDecision(regex=ParsingRegexKey.ASSIGN, key=ParsingStageKey.ASSIGNMENT),
            ],
            can_be_last_at_depth=0,
        )

    if key == ParsingStageKey.ASSIGNMENT:
        return ParsingStageConfiguration(
            decisions=[
                ParsingDecision(
                    regex=ParsingRegexKey.LETTER,
                    key=ParsingStageKey.VALUE_STRING,
                    pass_matched_char=True,
                ),
                ParsingDecision(
                    regex=ParsingRegexKey.NUMBER,
                    key=ParsingStageKey.VALUE_NUMBER,
                    pass_matched_char=True,
                ),
                ParsingDecision(
                    regex=ParsingRegexKey.QUOTE,
                    key=ParsingStageKey.VALUE_QUOTED_STRING,
                ),
                ParsingDecision(regex=ParsingRegexKey.OPEN_BRACE, key=ParsingStageKey.VALUE_BLOCK),
            ],
        )

    if key == ParsingStageKey.VALUE_STRING:
        inline_decisions = [
            ParsingDecision(
                default=True,
                status=ParsingStatus.QUIT,
                update_parent_block_stage_status=BlockStageStatus.LIST,
            ),
        ] if parent_stage.inline else [
            ParsingDecision(
                regex=ParsingRegexKey.NEWLINE,
                status=ParsingStatus.QUIT,
                update_parent_block_stage_status=BlockStageStatus.LIST,
            ),
            ParsingDecision(
                regex=ParsingRegexKey.HASHTAG,
                key=ParsingStageKey.COMMENT,
                update_parent_block_stage_status=BlockStageStatus.LIST,
            ),
        ]
        dict_parent_decision = [
            ParsingDecision(
                regex=ParsingRegexKey.ASSIGN,
                key=ParsingStageKey.ASSIGNMENT,
                update_parent_block_stage_status=BlockStageStatus.DICT,
            ),
        ] if parent_stage.block_stage_status == BlockStageStatus.UNKNOWN else []

        # The string can become a color function call
        color_decision = [
            ParsingDecision(
                regex=ParsingRegexKey.OPEN_BRACE,
                key=ParsingStageKey.BLOCK_COLOR,
                update_parent_block_stage_status=BlockStageStatus.LIST,
                if_data_function=(lambda data: (
                    isinstance(data, JONString) and
                    data.content in [color.value for color in JONColorType]
                )),
                replace_data_pass_function=(lambda data: (
                    JONColor(color_type=JONColorType(data.json())),
                    JONTokenType.FUNCTION,
                    BlockStageStatus.COLOR
                )),
                inline=True,
            ),
        ]

        return ParsingStageConfiguration(
            regex=ParsingRegexKey.WORD,
            decisions=color_decision + dict_parent_decision + inline_decisions,
            data_type=JONString,
            token_type=JONTokenType.STRING,
            can_be_last_at_depth=0,
        )

    if key == ParsingStageKey.VALUE_NUMBER:
        inline_decisions = [
            ParsingDecision(
                default=True,
                status=ParsingStatus.QUIT,
                update_parent_block_stage_status=BlockStageStatus.LIST,
            ),
        ] if parent_stage.inline else [
            ParsingDecision(
                regex=ParsingRegexKey.NEWLINE,
                status=ParsingStatus.QUIT,
                update_parent_block_stage_status=BlockStageStatus.LIST,
            ),
            ParsingDecision(
                regex=ParsingRegexKey.HASHTAG,
                key=ParsingStageKey.COMMENT,
                update_parent_block_stage_status=BlockStageStatus.LIST,
            ),
        ]
        dict_parent_decision = [
            ParsingDecision(
                regex=ParsingRegexKey.ASSIGN,
                key=ParsingStageKey.ASSIGNMENT,
                update_parent_block_stage_status=BlockStageStatus.DICT,
            ),
        ] if parent_stage.block_stage_status == BlockStageStatus.UNKNOWN else []

        return ParsingStageConfiguration(
            regex=ParsingRegexKey.DECIMAL_NUMBER,
            decisions=dict_parent_decision + inline_decisions,
            data_type=JONNumber,
            token_type=JONTokenType.NUMBER,
            can_be_last_at_depth=0,
        )

    if key == ParsingStageKey.VALUE_QUOTED_STRING:
        return ParsingStageConfiguration(
            regex=ParsingRegexKey.NO_QUOTE,
            decisions=[
                ParsingDecision(
                    regex=ParsingRegexKey.QUOTE,
                    key=ParsingStageKey.END_VALUE_QUOTED_STRING,
                    skip_whitespaces_count=True,
                ),
            ],
            data_type=JONQuotedString,
            token_type=JONTokenType.QUOTED_STRING,
            include_last_in_token=True,
        )

    if key == ParsingStageKey.END_VALUE_QUOTED_STRING:
        inline_decisions = [
            ParsingDecision(
                default=True,
                status=ParsingStatus.QUIT,
                update_parent_block_stage_status=BlockStageStatus.LIST,
            ),
        ] if parent_stage.inline else [
            ParsingDecision(
                regex=ParsingRegexKey.NEWLINE,
                status=ParsingStatus.QUIT,
                update_parent_block_stage_status=BlockStageStatus.LIST,
            ),
            ParsingDecision(
                regex=ParsingRegexKey.HASHTAG,
                key=ParsingStageKey.COMMENT,
                update_parent_block_stage_status=BlockStageStatus.LIST,
            ),
        ]
        dict_parent_decision = [
            ParsingDecision(
                regex=ParsingRegexKey.ASSIGN,
                key=ParsingStageKey.ASSIGNMENT,
                update_parent_block_stage_status=BlockStageStatus.DICT,
            ),
        ] if parent_stage.block_stage_status == BlockStageStatus.UNKNOWN else []

        return ParsingStageConfiguration(
            decisions=dict_parent_decision + inline_decisions,
            can_be_last_at_depth=0,
        )

    if key == ParsingStageKey.VALUE_BLOCK:
        inline_decisions = [] if parent_stage.inline else [
            ParsingDecision(regex=ParsingRegexKey.NEWLINE, key=ParsingStageKey.BLOCK_LIST),
            ParsingDecision(regex=ParsingRegexKey.HASHTAG, key=ParsingStageKey.COMMENT_START_BLOCK),
        ]

        return ParsingStageConfiguration(
            decisions=(inline_decisions + [
                ParsingDecision(
                    default=True,
                    key=ParsingStageKey.BLOCK_LIST,
                    inline=True,
                ),
            ]),
        )

    if key == ParsingStageKey.END_BLOCK:
        # The stage is still in its natural parent so its grand-parent must be evaluated
        grand_parent_is_inline = parent_stage.parent is not None and parent_stage.parent.inline
        inline_decisions = [
            ParsingDecision(default=True, status=ParsingStatus.SUPERQUIT),
        ] if grand_parent_is_inline else [
            ParsingDecision(regex=ParsingRegexKey.NEWLINE, status=ParsingStatus.SUPERQUIT),
            ParsingDecision(regex=ParsingRegexKey.HASHTAG, key=ParsingStageKey.COMMENT_END_BLOCK),
        ]
        return ParsingStageConfiguration(
            decisions=inline_decisions,
            can_be_last_at_depth=1,
        )

    if key == ParsingStageKey.COMMENT:
        return ParsingStageConfiguration(
            regex=ParsingRegexKey.NO_WHITESPACE,
            decisions=[
                ParsingDecision(regex=ParsingRegexKey.NEWLINE, status=ParsingStatus.QUIT),
                ParsingDecision(
                    regex=ParsingRegexKey.NO_WHITESPACE,
                    key=ParsingStageKey.COMMENT,
                    skip_whitespaces_count=True,
                ),
            ],
            token_type=JONTokenType.COMMENT,
            can_be_last_at_depth=0,
        )

    if key == ParsingStageKey.COMMENT_START_BLOCK:
        return ParsingStageConfiguration(
            regex=ParsingRegexKey.NO_WHITESPACE,
            decisions=[
                ParsingDecision(regex=ParsingRegexKey.NEWLINE, key=ParsingStageKey.BLOCK_LIST),
                ParsingDecision(
                    regex=ParsingRegexKey.NO_WHITESPACE,
                    key=ParsingStageKey.COMMENT_START_BLOCK,
                    skip_whitespaces_count=True,
                ),
            ],
            token_type=JONTokenType.COMMENT,
        )

    if key == ParsingStageKey.COMMENT_END_BLOCK:
        return ParsingStageConfiguration(
            regex=ParsingRegexKey.NO_WHITESPACE,
            decisions=[
                ParsingDecision(regex=ParsingRegexKey.NEWLINE, status=ParsingStatus.SUPERQUIT),
                ParsingDecision(
                    regex=ParsingRegexKey.NO_WHITESPACE,
                    key=ParsingStageKey.COMMENT_END_BLOCK,
                    skip_whitespaces_count=True,
                ),
            ],
            token_type=JONTokenType.COMMENT,
            can_be_last_at_depth=1,
        )

    return ParsingStageConfiguration()


class ParsingStage:
    """Generic JON parsing stage class"""

    def __init__(
            self,
            queue: ParsingQueue,
            validation_errors: List[ParsingValidationError],
            tokens: List[JONToken],
            config_key: ParsingStageKey = ParsingStageKey.BLOCK_LIST,
            parent: Optional[ParsingStage] = None,
            data: Optional[JONData] = None,
            initial_char: Optional[str] = None,
            is_end = False,
            block_stage_status = BlockStageStatus.UNKNOWN,
            inline = False,
        ) -> None:
        self._queue = queue
        self._validation_errors = validation_errors
        self._tokens = tokens
        self.parent = parent
        self._config = stage_configuration(config_key, self.parent)
        self.is_end = is_end
        self.block_stage_status = block_stage_status
        self.inline = inline

        if parent is None:
            self.depth = -1
        else:
            self.depth = self.parent.depth + 1

        if data is not None:
            self.data = data
        elif self._config.data_type is not None:
            if initial_char is not None:
                self.data = self._config.data_type(initial_char)
            else:
                self.data = self._config.data_type()
            self.parent.data.attach(self.data, key=self._config.data_key)
        else:
            self.data = None

    def next(self) -> Tuple[Optional[ParsingStage], bool]:
        """
        Continue parsing and progress accordingly to the parsing result. Returns the next stage (or
        None) and a boolean that indicates if the parsing status is SUPERQUIT
        """

        parsing_status, next_stage = self._parse()

        if parsing_status == ParsingStatus.CONTINUE:
            return next_stage, False

        if parsing_status == ParsingStatus.QUIT:
            return None, False

        if parsing_status == ParsingStatus.SUPERQUIT:
            return None, True

        # Parsing status is ENTER
        child_stage = next_stage
        while child_stage is not None:
            child_stage, is_superquit = child_stage.next()

        if is_superquit:
            return None, False

        return self.next()

    def update_block_stage_status(self, block_stage_status: BlockStageStatus) -> None:
        """Update the block stage status of a stage that has an unknown status"""

        if self.block_stage_status == BlockStageStatus.UNKNOWN:
            self.block_stage_status = block_stage_status

            # Change data for non-default DICT Block stage status
            if block_stage_status == BlockStageStatus.DICT:
                new_data = self.data.to_dict()
                if new_data is not None:
                    self._config = stage_configuration(ParsingStageKey.BLOCK_DICT, self.parent)
                    self.data = new_data
                    if self.parent is not None:
                        self.parent.data.replace(child=new_data)

    def _parse(self) -> Tuple[ParsingStatus, Optional[ParsingStage]]:
        """Continue parsing"""

        # If parsing has ended, exit immediately
        if self.is_end:
            if self.parent is not None:
                self.parent.is_end = True
            return ParsingStatus.QUIT, None

        if self._config.force_enter_in is not None:
            child_stage = ParsingStage(
                queue=self._queue,
                validation_errors=self._validation_errors,
                tokens=self._tokens,
                config_key=self._config.force_enter_in,
                parent=self,
                inline=self.inline,
            )
            return ParsingStatus.ENTER, child_stage

        self._queue.save()
        self._queue.save_position()
        char = self._queue.next()

        # Continue while parsed char are accepted in the stage
        while char is not None and PARSING_REGEXES[self._config.regex].match(char):
            if self.data is not None:
                self._queue.save()
                can_accept_more_chars = self.data.add_char(char)

                # If the data cannot accept more chars, exit the loop
                if not can_accept_more_chars:
                    break
            char = self._queue.next()

        # Create semantic token linked to parsed chars
        if self._config.token_type is not None:
            token_positions = self._queue.get_positions(
                exclude_last=not self._config.include_last_in_token,
            )
            self._tokens.append(JONToken(
                positions=token_positions,
                token_type=self._config.token_type,
            ))

        # Continue while parsed char are whitespaces
        self._queue.save_position()
        whitespaces = {
            ' ': 0,
            '\t': 0,
        }
        while char in whitespaces:
            whitespaces[char] += 1
            char = self._queue.next()

        whitespaces_positions = self._queue.get_positions(exclude_last=True)

        # Count the number of whitespaces
        whitespaces_count = whitespaces[' '] + 4 * whitespaces['\t']
        if self._config.has_indent:
            # Check for inconsistent use of tabs and spaces
            if whitespaces[' '] != 0 and whitespaces['\t'] != 0:
                self._validation_errors.append(ParsingValidationError(
                    "W001",
                    whitespaces_positions
                ))
        # Check for use of tabs without indent
        elif whitespaces['\t'] != 0:
            self._validation_errors.append(ParsingValidationError(
                "W005",
                whitespaces_positions
            ))

        # Deal with potential end of the queue
        if char is None:
            if whitespaces_count != 0:
                self._validation_errors.append(ParsingValidationError(
                    "W002",
                    whitespaces_positions,
                ))

            self.parent.is_end = True

            last_position = self._queue.get_position()
            if (
                self._config.can_be_last_at_depth is None or
                self._config.can_be_last_at_depth != self.depth
            ):
                self._validation_errors.append(ParsingValidationError(
                    "E003",
                    (last_position, last_position),
                ))
            return ParsingStatus.QUIT, None

        for decision in self._config.decisions:
            if (
                (PARSING_REGEXES[decision.regex].match(char) or decision.default) and
                (decision.if_data_function is None or decision.if_data_function(self.data))
            ):
                # Eventually update the parent block stage status
                if decision.update_parent_block_stage_status is not None:
                    self.parent.update_block_stage_status(decision.update_parent_block_stage_status)

                # Restore the queue if marked as default
                if decision.default:
                    self._queue.restore()

                # Check number of whitespaces
                if not decision.skip_whitespaces_count and not decision.default:
                    if char == "\n":
                        if whitespaces_count != 0:
                            self._validation_errors.append(ParsingValidationError(
                                "W002",
                                whitespaces_positions,
                            ))
                    elif self._config.has_indent:
                        if whitespaces_count != 4 * (self.depth - (1 if char == '}' else 0)):
                            self._validation_errors.append(ParsingValidationError(
                                "W003",
                                whitespaces_positions,
                            ))
                    elif whitespaces_count != 1:
                        self._validation_errors.append(ParsingValidationError(
                            "W004",
                            whitespaces_positions,
                        ))

                # Data is replaced and passed if the decision requires to
                pass_data = False
                block_stage_status = BlockStageStatus.UNKNOWN
                if decision.replace_data_pass_function is not None:
                    pass_data = True
                    self.data, new_token_type, block_stage_status = (
                        decision.replace_data_pass_function(self.data)
                    )

                    if self._tokens:
                        self._tokens[-1].token_type = new_token_type

                    if self.parent is not None:
                        self.parent.data.replace(child=self.data)

                next_stage = None
                if decision.status in [ParsingStatus.CONTINUE, ParsingStatus.ENTER]:
                    next_stage_is_inline = decision.inline or self.parent.inline

                    next_stage = ParsingStage(
                        queue=self._queue,
                        validation_errors=self._validation_errors,
                        tokens=self._tokens,
                        config_key=decision.key,
                        parent=(self.parent if ParsingStatus.CONTINUE else self),
                        data=(self.data if pass_data else None),
                        block_stage_status=block_stage_status,
                        initial_char=(char if decision.pass_matched_char else None),
                        inline=next_stage_is_inline,
                    )
                return decision.status, next_stage

        # Deal with unexpected chars
        last_position = self._queue.get_position()
        if char == "\n":
            self._validation_errors.append(ParsingValidationError(
                "E001",
                (last_position, last_position),
            ))
        else:
            self._queue.go_to_new_line()
            self._validation_errors.append(ParsingValidationError(
                "E002",
                (last_position, last_position),
            ))
        return ParsingStatus.QUIT, None
