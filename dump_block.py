#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dump_block.py

Dump the binary of the img file for debugging.  Forwards most of options
to the underlying xxd command, with a few controlled exceptions.

USAGE: `./dump_block.py --all FILE`

USAGE: `./dump_block.py 1`

USAGE: `./dump_block.py --help`
"""

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import subprocess
import sys
from argparse import ArgumentParser, ArgumentTypeError, RawTextHelpFormatter
from enum import IntEnum
from pathlib import Path
from typing import List, Optional

__author__ = "Vincent Lin"

IMG_FILE = Path("cs111-base.img")

BLACK = "\x1b[30m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
END = "\x1b[0m"

NUM_BLOCKS = 1024
BLOCK_SIZE = 1024


class BlockNames(IntEnum):
    BOOT = 0
    SUPERBLOCK = 1
    DESCRIPTOR = 2
    BLOCK_BITMAP = 3
    INODE_BITMAP = 4
    INODE_TABLE = 5
    ROOT_DIR = 21
    LOST_AND_FOUND = 22
    HELLO_WORLD = 23


INODE_TABLE_BLOCKNOS = range(5, 21)


def cast_int(value: str) -> int:
    if value.startswith("0x"):
        return int(value, 16)
    if value.startswith("0o"):
        return int(value, 8)
    if value.startswith("0b"):
        return int(value, 2)
    return int(value)


def valid_blockno(value: str) -> int:
    # First try to resolve it as a block name.
    try:
        blockno = BlockNames[value.upper()]
        if blockno is None:
            raise ArgumentTypeError(
                f"{value!r} is not a recognized block name.")
        return blockno.value
    except KeyError:
        pass

    # Then interpret it as a number.
    as_int = cast_int(value)
    if as_int not in range(0, NUM_BLOCKS):
        raise ArgumentTypeError(
            f"{value} is not in the range [0, {NUM_BLOCKS}).")
    return as_int


def valid_offset(value: str) -> int:
    as_int = cast_int(value)
    if as_int not in range(0, BLOCK_SIZE):
        raise ArgumentTypeError(
            f"{value} is not in the range [0, {BLOCK_SIZE}).")
    return as_int


RECOGNIZED_BLOCK_NAMES = "\n".join(f"  {e.name} = {e.value}"
                                   for e in BlockNames)

DESCRIPTION = f"""\
Dump the binary of the specified block.

Recognized block names (case-insensitive) are:

{RECOGNIZED_BLOCK_NAMES}

Example usages:

    * Viewing your full inode bitmap:
        ./dump_block.py inode_bitmap --binary

    * Checking a specific struct field, like u16 s_magic:
        ./dump_block.py superblock -o 0x37 -l 2

    * Forwarding formatting options to xxd:
        ./dump_block.py 21 -g 1 -c 24
"""

parser = ArgumentParser(prog=sys.argv[0],
                        description=DESCRIPTION,
                        formatter_class=RawTextHelpFormatter)

parser.add_argument("block_num", metavar="BLOCK", nargs="?",
                     type=valid_blockno, default=BlockNames.SUPERBLOCK.value,
                     help="number or name of block to dump")

parser.add_argument("-a", "--all", metavar="FILE", dest="dump_file",
                    help=("dump the entire img to a file "
                         "(ignores most other options)"))

# Added -s as an alias to be consistent with xxd's offset option.  Also,
# intercepting it here will make sure it doesn't override our controlled
# -o option.
parser.add_argument("-o", "-s", "--offset", metavar="NBYTES",
                    type=valid_offset, default=0,
                    help="offset within the block")

parser.add_argument("-l", "--length", metavar="NBYTES",
                    type=valid_offset, default=1024,
                    help="amount of block to dump")

parser.add_argument("-q", "--quiet", action="store_true",
                    help="output only what xxd does")

parser.add_argument("-b", "--binary", action="store_true",
                    help="use binary instead of hexadecimal")


def run(script: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(script, shell=True, capture_output=True, check=False)


def make_img() -> bool:
    run("make")
    run("./ext2-create")
    return IMG_FILE.exists()


def calc_abs_offset(block_num: int, offset: int) -> int:
    return (block_num * BLOCK_SIZE) + offset


def bound_length(length: int, offset: int) -> int:
    return min(length, BLOCK_SIZE - offset)


def prepare_xxd(absolute_offset: int, length: int, binary: bool,
                unknowns: List[str]) -> str:
    # Forward custom xxd arguments to xxd.
    custom_args = " ".join(unknowns)
    command = (f"xxd -s {absolute_offset} -l {length} "
               f"{'-b' if binary else ''} {custom_args} {IMG_FILE} ")
    return command


def get_block_name(block_num: int) -> Optional[str]:
    # Special case: the inode table spans multiple blocks.
    if block_num in INODE_TABLE_BLOCKNOS:
        return BlockNames.INODE_TABLE.name

    # Otherwise consult the enum.
    try:
        return BlockNames(block_num).name
    except ValueError:
        return None


def dump_all(dump_file: Path, binary: bool, quiet: bool) -> None:
    with dump_file.open("wt", encoding="utf-8") as fp:
        for block_num in range(NUM_BLOCKS):
            absolute_offset = calc_abs_offset(block_num, 0)
            command = prepare_xxd(absolute_offset, BLOCK_SIZE, binary, [])

            output = run(command).stdout.decode()

            if not quiet:
                header = f"BLOCK {block_num:04}"
                name = get_block_name(block_num)
                if name is not None:
                    header += f" ({name})"
                fp.write(header + "\n")

            fp.write(output)
            fp.write("\n")


def main() -> None:
    namespace, unknowns = parser.parse_known_args()
    dump_file = namespace.dump_file
    binary = namespace.binary
    quiet = namespace.quiet

    if dump_file is not None:
        dump_all(Path(dump_file), binary, quiet)
        return

    block_num = namespace.block_num
    offset = namespace.offset
    length = namespace.length

    # Don't let length go beyond a block.
    length = bound_length(length, offset)

    # Ensure that the img file exists.
    if not IMG_FILE.exists() and not make_img():
        sys.stderr.write(f"Could not generate {IMG_FILE}, aborting.\n")
        sys.exit(1)

    absolute_offset = calc_abs_offset(block_num, offset)
    command = prepare_xxd(absolute_offset, length, binary, unknowns)

    # Echo the underlying command.
    if not quiet:
        print(f"{BLACK}{command}{END}")

    output = run(command).stdout.decode()

    # Format the header.
    if not quiet:
        # Attempt to get name information about this current block.
        name = get_block_name(block_num)
        slicing = f"{offset}:{offset+length}"
        location = f"{block_num:04} @ {hex(absolute_offset)}"
        header = f"BLOCK {location} [{slicing}]"
        suffix = "" if name is None else f" ({name})"
        print(f"{GREEN}{header}{END}{YELLOW}{suffix}{END}")

    print(output)


if __name__ == "__main__":
    main()
