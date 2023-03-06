#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_dump.py

Compare the output of your `dumpe2fs cs111-base.img` file to the
completed example in the implementation guide posted by TA Can at
https://piazza.com/class/lcjl27z4agp66l/post/400.
"""

# pylint: disable=all

import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

__author__ = "Vincent Lin"

EXAMPLE_DUMP_TXT = Path("dump_example.txt")

RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
END = "\x1b[0m"


def run(script: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(script, capture_output=True, shell=True, check=True)


def get_your_dump() -> str:
    run("make")
    run("./ext2-create")
    return run("dumpe2fs cs111-base.img").stdout.decode()


def get_example_dump() -> str:
    with EXAMPLE_DUMP_TXT.open("rt", encoding="utf-8") as txt:
        return txt.read()


def parse_dump_datetime(string: str) -> datetime:
    return datetime.strptime(string, "%a %b %d %H:%M:%S %Y")


def format_dump_datetime(dt: datetime) -> str:
    without_day = dt.strftime("%a %b {day:2} %H:%M:%S %Y")
    string = without_day.format(day=dt.day)  # Must NOT be zero-padded.
    return string


def compare_fs_lines(example: List[str], yours: List[str]) -> bool:
    def print_field(name: str, example: str, yours: str) -> None:
        # Right-fill to match spacing of original dump.
        name_prefix = (name + ":").ljust(27)
        print(f"{name_prefix}{GREEN}{example}{END}", end="")
        if yours != example:
            print(f" != {RED}{yours}{END}")
        else:
            print()

    diff_found = False
    last_write_time: datetime = datetime.now()  # Placeholder.

    for example_line, your_line in zip(example, yours):

        example_parts = example_line.split(":", maxsplit=1)
        field_name = example_parts[0]
        correct_value = example_parts[1].strip()
        your_value = your_line.split(":", maxsplit=1)[1].strip()

        # Process special datetime values.  These will be different from
        # the ones in the example, but they must be correct with respect
        # to each other (last write == last checked, next check == last
        # checked + 1).

        if field_name == "Last write time":
            last_write_time = parse_dump_datetime(your_value)
            correct_value = format_dump_datetime(last_write_time)

        elif field_name == "Last checked":
            correct_value = format_dump_datetime(last_write_time)

        elif field_name == "Next check after":
            expected_dt = last_write_time + timedelta(seconds=1)
            correct_value = format_dump_datetime(expected_dt)

        # A mismatch!
        elif example_line != your_line:
            diff_found = True

        print_field(field_name, correct_value, your_value)

    # Chances are you probably did not use `current_time` for fields.
    if last_write_time.year < datetime.now().year:
        print(f"{YELLOW}WARNING: Your datetime values look off. Did you "
              f"remember to use `current_time`?{END}")

    return not diff_found


# Code paraphrased from ChatGPT.
def replace_capturing_groups(regexp: str) -> str:
    # Matches unnamed capturing groups.
    group_searcher = re.compile(r"[^\\](\(.+?(?:[^\\]\)))")
    result = regexp

    # Replace each capturing group with a placeholder.
    placeholder_num = 0
    while True:

        # Find the next capturing group in the regex.
        match = group_searcher.search(result)
        if match is None:
            break

        # Replace the capturing group with a placeholder.
        placeholder = f'{{{placeholder_num}}}'
        start, stop = match.span(1)
        result = result[:start] + placeholder + result[stop:]

        placeholder_num += 1

    # Strip escape characters.
    return result.replace("\\", "")


def compare_group_line(example: str, yours: str, regexp: str) -> bool:
    diff_found = False

    def get_expr(example: str, yours: Optional[str] = None) -> str:
        expr = f"{GREEN}{example}{END}"
        if yours is None or yours != example:
            expr += f" != {RED}{yours}{END}"
            nonlocal diff_found
            diff_found = True
        return expr

    example_match = re.match(regexp, example)
    if example_match is None:
        raise ValueError("Regex parsing shouldn't have failed on the example.")
    example_groups = example_match.groups()

    your_match = re.match(regexp, yours)
    if your_match is None:
        your_groups = [""] * len(example_groups)
    else:
        your_groups = your_match.groups()

    template = replace_capturing_groups(regexp)

    # Fill out all the placeholders
    expressions = [get_expr(e, y) for e, y in
                   zip(example_groups, your_groups)]
    formatted = template.format(*expressions)
    print(formatted)

    return not diff_found


def compare_group_lines(example: List[str], yours: List[str]) -> bool:
    passing = True

    regexps = (
        r"Group (\d+): \(Blocks (\d+-\d+)\)",
        r"  Primary superblock at (\d+), Group descriptors at (\d+-\d+)",
        r"  Block bitmap at (\d+) \(\+(\d+)\)",
        r"  Inode bitmap at (\d+) \(\+(\d+)\)",
        r"  Inode table at (\d+-\d+) \(\+(\d+)\)",
        r"  (\d+) free blocks, (\d+) free inodes, (\d+) directories",
        r"  Free blocks: (\d+-\d+)",
        r"  Free inodes: (\d+-\d+)"
    )

    for example_line, your_line, regexp in zip(example, yours, regexps):
        if not compare_group_line(example_line, your_line, regexp):
            passing = False

    # Make a note about the consistency of free blocks/inodes and how
    # they don't mean much if you haven't gotten to implementing the
    # bitmaps yet.
    if not passing:
        print(f"{YELLOW}NOTE: If you haven't finished implementing bitmaps, "
              f"incorrect & inconsistent free block/inodes are expected.{END}")

    return passing


def main() -> int:
    example_lines = get_example_dump().splitlines()
    your_lines = get_your_dump().splitlines()

    example_fs_lines = example_lines[:31]
    example_group_lines = example_lines[33:]
    your_fs_lines = your_lines[:31]
    your_group_lines = your_lines[33:]

    diff_passed = compare_fs_lines(example_fs_lines, your_fs_lines)
    print("\n")
    group_passed = compare_group_lines(example_group_lines, your_group_lines)

    return 0 if diff_passed and group_passed else 1


if __name__ == "__main__":
    sys.exit(main())
