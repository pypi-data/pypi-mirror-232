r"""
    jon.cli
    ~~~~~~~

    JON Command Line Interface tools

    :copyright: (c) 2023, Justin Béra (@just1not2) <me@just1not2.org>
    :license: Apache License 2.0 (see LICENSE or https://www.apache.org/licenses/LICENSE-2.0.txt
"""
__all__ = [
    "exit_error",
    "lint",
]

import argparse
import os
import sys
from jon import JONValidationRuleLevel, validate


def exit_error(message: str) -> None:
    """Exit with error"""

    sys.stderr.write(f"jon-lint: error: {message}\n")
    sys.exit(1)


def lint() -> None:
    """Command to lint JON files"""

    parser = argparse.ArgumentParser(
        prog="jon-lint",
        description="Lint JON files with the command line",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        help="recursively lint directories",
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "-e",
        "--only-errors",
        help="skip warnings during linting",
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "path",
        help="file or directory to lint",
        default=".",
    )
    args = parser.parse_args()

    files = []

    if os.path.isfile(args.path):
        files.append(args.path)

    elif os.path.isdir(args.path):
        directories = [args.path]
        while directories:
            directory = directories.pop()
            file_or_dir_list = os.listdir(directory)

            for file_or_dir in file_or_dir_list:
                file_or_dir_path = f"{directory}/{file_or_dir}"
                if (
                    os.path.isfile(file_or_dir_path) and
                    (file_or_dir.endswith(".jon") or file_or_dir.endswith(".txt"))
                ):
                    files.append(file_or_dir_path)
                elif args.recursive and os.path.isdir(file_or_dir_path):
                    directories.append(file_or_dir_path)

    else:
        exit_error(f"'{args.path}' is not a file or a directory")

    errors_count = {
        "error": 0,
        "warning": 0,
    }

    for file in files:
        file_content = ""
        try:
            with open(file, mode="r", encoding="utf-8-sig") as file_object:
                file_content = file_object.read()
        except IOError as err:
            exit_error(f"could not open '{file}': {err}")

        validation_errors = validate(file_content)
        if not validation_errors:
            continue

        if args.only_errors:
            skip_file = True
            for validation_error in validation_errors:
                if validation_error.rule.level == JONValidationRuleLevel.ERROR:
                    skip_file = False
                    break
            if skip_file:
                continue

        print(f"********** {file}")

        for validation_error in validation_errors:
            if validation_error.rule.level == JONValidationRuleLevel.ERROR:
                errors_count["error"] += 1
                print(validation_error.stringify())

            elif (
                validation_error.rule.level == JONValidationRuleLevel.WARNING
                and not args.only_errors
            ):
                errors_count["warning"] += 1
                print(validation_error.stringify())


    print("\n---------------------------- RECAP ----------------------------")
    errors_count_string = f"ERRORS={errors_count['error']}"
    warnings_count_string = f", WARNINGS={errors_count['warning']}" if not args.only_errors else ""
    print(f"{errors_count_string}{warnings_count_string}")

    if errors_count['error'] > 0:
        sys.exit(1)
