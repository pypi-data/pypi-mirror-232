# Copyright (c) 2023, Justin Béra (@just1not2) <me@just1not2.org>
# Apache License 2.0 (see LICENSE or https://www.apache.org/licenses/LICENSE-2.0.txt

import unittest
import yaml
from jon import get_tokens, load, validate
from jon import JONColor, JONDict, JONList, JONNumber, JONQuotedString, JONString


TESTS = {}


##################            PARSING            ##################

def parse_data(reporter, json, data):
    if isinstance(json, str) and json.startswith('color('):
        reporter.assertIsInstance(data, JONColor, "Data should be a JONColor")
        reporter.assertEqual(json, data.json(), "Color string values do not match")
    elif isinstance(json, str):
        reporter.assertIsInstance(data, JONString, "Data should be a JONString")
        if json != "" and json[0] == "\"":
            reporter.assertIsInstance(data, JONQuotedString, "Data should be a JONQuotedString")
        reporter.assertEqual(json, data.json(), "String values do not match")

    elif isinstance(json, (int, float)):
        reporter.assertIsInstance(data, JONNumber, "Data should be a JONNumber")
        reporter.assertEqual(json, data.json(), "Number values do not match")

    elif isinstance(json, list):
        reporter.assertIsInstance(data.content, list, "Data content should be a list")
        reporter.assertEqual(len(json), len(data.content), "Lists do not have the same length")

        data_is_list = json == [] or not isinstance(json[0], dict)
        reporter.assertIsInstance(data, JONList if data_is_list else JONDict, "Data block type is incorrect")

        for i in range(len(json)):
            if data_is_list:
                parse_data(reporter, json[i], data.content[i])
            else:
                reporter.assertIsInstance(data.content[i], tuple, "Data content element should be a tuple")
                key = list(json[i].keys())[0]
                parse_data(reporter, key, data.content[i][0])
                parse_data(reporter, json[i][key], data.content[i][1])


def parsing_test(reporter):
    test_case_parsing = TESTS["parsing"]
    document = None
    with open(f"tests/files/parsing.jon", mode="r", encoding="utf-8") as test_file:
        document = load(test_file.read())
        parse_data(reporter, test_case_parsing, document)


class TestParsing(unittest.TestCase):

    def test(self):
        parsing_test(self)


##################          VALIDATION          ##################

def validate_test(reporter, key):
    test_case = TESTS["validation"][key]
    validation_errors = []
    with open(f"tests/files/validation.{key}.jon", mode="r", encoding="utf-8") as test_file:
        validation_errors = validate(test_file.read())

    for i in range(len(validation_errors)):
        reporter.assertEqual(
            test_case[i]["code"],
            validation_errors[i].rule.key,
            msg="Error codes do not match",
        )

        positions = validation_errors[i].positions
        reporter.assertEqual(
            test_case[i]["positions"],
            [[positions[0][0], positions[0][1]], [positions[1][0], positions[1][1]]],
            msg="Error positions do not match",
        )


class TestValidation(unittest.TestCase):

    def test_indent(self):
        validate_test(self, "indent")

    def test_end_of_line(self):
        validate_test(self, "end-of-line")

    def test_inline(self):
        validate_test(self, "inline")

    def test_space_separation(self):
        validate_test(self, "space-separation")

    def test_block(self):
        validate_test(self, "block")
    
    def test_color(self):
        validate_test(self, "color")


##################            TOKENS            ##################

def tokens_test(reporter):
    test_case_tokens = TESTS["tokens"]
    tokens = []
    with open(f"tests/files/tokens.jon", mode="r", encoding="utf-8") as test_file:
        tokens = get_tokens(test_file.read())

    reporter.assertEqual(len(tokens), len(test_case_tokens), "Token lists do not have the same length")

    for i in range(len(tokens)):
        reporter.assertEqual(
            test_case_tokens[i]["type"],
            tokens[i].token_type.value,
            msg="Token types do not match",
        )

        positions = tokens[i].positions
        reporter.assertEqual(
            test_case_tokens[i]["positions"],
            [[positions[0][0], positions[0][1]], [positions[1][0], positions[1][1]]],
            msg="Token positions do not match",
        )


class TestTokens(unittest.TestCase):

    def test(self):
        tokens_test(self)


if __name__ == "__main__":
    with open("tests/tests.yaml", mode="r", encoding="utf-8") as tests_file:
        TESTS = yaml.safe_load(tests_file)

    unittest.main()
