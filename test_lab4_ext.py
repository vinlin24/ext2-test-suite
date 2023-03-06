#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_lab4_ext.py

Extended unit tester for W23 COM SCI 111 Lab 4: Hey! I'm Filing Here.

USAGE (with handout): `python -m unittest`

USAGE (isolated): `./test_lab4_ext.py`
"""

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-public-methods

import os
import stat
import subprocess
import sys
import unittest
from enum import IntEnum
from pathlib import Path

__author__ = "Vincent Lin"

# NOTE: Use .lstat() and not .stat() on Path objects to get the stat
# result for files and symlinks alike (i.e. do NOT resolve symlinks).


def run(script: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(script, shell=True, capture_output=True, check=False)


class FileType(IntEnum):
    DIRECTORY = stat.S_IFDIR
    REGULAR = stat.S_IFREG
    SYMLINK = stat.S_IFLNK


class TestMountedStats(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        run("make")
        run("./ext2-create")
        if not Path("cs111-base.img").exists():
            sys.stderr.write("Could not generate img file, aborting.\n")
            sys.exit(1)
        run("mkdir mnt")
        run("sudo mount -o loop cs111-base.img mnt")

        cls.root_path = Path("mnt")
        cls.lost_and_found_path = cls.root_path / "lost+found"
        cls.hello_world_path = cls.root_path / "hello-world"
        cls.hello_path = cls.root_path / "hello"

        cls.ls_lines = run("ls -ain mnt").stdout.decode().splitlines()

    @classmethod
    def tearDownClass(cls) -> None:
        run("sudo umount mnt")
        run("rmdir mnt")
        run("make clean")

    def testRootExistence(self) -> None:
        self.assertTrue(self.root_path.exists())

    def testLostAndFoundExistence(self) -> None:
        self.assertTrue(self.lost_and_found_path.exists())

    def testHelloWorldExistence(self) -> None:
        self.assertTrue(self.hello_world_path.exists())

    def testHelloExistence(self) -> None:
        self.assertTrue(self.hello_path.exists())

    def _testMode(self, path: Path, file_type: FileType, octal_perms: int
                  ) -> None:
        if not path.exists():
            self.skipTest(f"{path} does not exist.")
        mode = path.lstat().st_mode
        self.assertEqual(stat.S_IFMT(mode), file_type.value,
                         f"Expected {path} to be a {file_type.name}.")
        self.assertEqual(stat.S_IMODE(mode), octal_perms,
                         f"Expected octal {oct(octal_perms)[2:]} "
                         f"({stat.filemode(mode)}) permissions for {path}")

    def testRootMode(self) -> None:
        self._testMode(self.root_path, FileType.DIRECTORY, 0o755)

    def testLostAndFoundMode(self) -> None:
        self._testMode(self.lost_and_found_path, FileType.DIRECTORY, 0o755)

    def testHelloWorldMode(self) -> None:
        self._testMode(self.hello_world_path, FileType.REGULAR, 0o644)

    def testHelloMode(self) -> None:
        self._testMode(self.hello_path, FileType.SYMLINK, 0o644)

    def _testIDs(self, path: Path, uid: int, gid: int) -> None:
        if not path.exists():
            self.skipTest(f"{path} does not exist.")
        self.assertEqual(path.lstat().st_uid, uid,
                         f"Expected a UID of {uid} for {path}.")
        self.assertEqual(path.lstat().st_gid, gid,
                         f"Expected a GID of {gid} for {path}.")

    def testRootIDs(self) -> None:
        self._testIDs(self.root_path, 0, 0)

    def testLostAndFoundIDs(self) -> None:
        self._testIDs(self.lost_and_found_path, 0, 0)

    def testHelloWorldIDs(self) -> None:
        self._testIDs(self.hello_world_path, 1000, 1000)

    def testHelloIDs(self) -> None:
        self._testIDs(self.hello_path, 1000, 1000)

    def testRootNumEntries(self) -> None:
        self.assertEqual(len(self.ls_lines), 6)  # +1 from "total" line.

    def testRootLinkage(self) -> None:
        cdir_inum, *_, cdir_file = self.ls_lines[1].split()
        pdir_inum, *_, pdir_file = self.ls_lines[2].split()

        p = run("ls -ai1 | awk 'NR==1{print $1}'")
        lab_dir_inum = p.stdout.decode().rstrip()

        self.assertEqual(cdir_file, ".")
        self.assertEqual(pdir_file, "..")
        self.assertEqual(cdir_inum, "2")
        self.assertEqual(pdir_inum, lab_dir_inum)

    def testHelloWorldContent(self) -> None:
        path = self.hello_world_path
        if not path.exists():
            self.skipTest(f"{path} does not exist.")
        with path.open("rt", encoding="utf-8") as hello_world:
            content = hello_world.read()
        self.assertEqual(content, "Hello world\n")

    def testHelloContent(self) -> None:
        path = self.hello_path
        if not path.exists():
            self.skipTest(f"{path} does not exist.")
        self.assertEqual(os.readlink(path), "hello-world")

    def _testFileSize(self, path: Path, expected_bytes: int) -> None:
        if not path.exists():
            self.skipTest(f"{path} does not exist")
        size = path.lstat().st_size
        self.assertEqual(size, expected_bytes)

    def testRootSize(self) -> None:
        self._testFileSize(self.root_path, 1024)

    def testLostAndFoundSize(self) -> None:
        self._testFileSize(self.lost_and_found_path, 1024)

    def testHelloWorldSize(self) -> None:
        self._testFileSize(self.hello_world_path, 12)

    def testHelloSize(self) -> None:
        self._testFileSize(self.hello_path, 11)

    def testFsckAllPass(self) -> None:
        fsck = run("fsck.ext2 -n cs111-base.img")
        self.assertEqual(fsck.returncode, 0)
        last_line = fsck.stdout.decode().splitlines()[-1]
        self.assertEqual(
            last_line,
            "cs111-base: 13/128 files (0.0% non-contiguous), 24/1024 blocks")


if __name__ == "__main__":
    unittest.main()
