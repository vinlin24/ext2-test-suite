#!/usr/bin/env bash
# Script to automate setting up the test suite in your lab4 directory.

# USAGE: ./setup.sh /path/to/lab4

if [ $# -eq 0 ]; then
    echo >&2 "$0: Specify the directory to set up in."
    exit 1
fi

lab_dir="$1"

if [ ! -d "$lab_dir" ]; then
    echo >&2 "$0: ${lab_dir} is not a valid directory path."
    exit 1
fi

# Overengineering be like.
tarball_name=$(sed -En 's/all: (.+)$/\1/p' Makefile)
suite_files=$(sed -En 's/SUITE_FILES = (.+)/\1/p' Makefile | tr ' ' '\n')

ignore_additions="\n# Test suite\n*.tar\n${suite_files}"

# Actual setup sequence.
make &&
    cp "$tarball_name" "$lab_dir" &&
    cd "$lab_dir" &&
    tar -xf "$tarball_name" &&
    echo -e "$ignore_additions" >>.gitignore

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
END=$(tput sgr0)

if [ $? -eq 0 ]; then
    echo -n "${GREEN}The lab suite has been set up in ${lab_dir}. "
    echo "Happy coding!${END}"
else
    echo >&2 "${RED}Something went wrong...${END}"
    exit 1
fi
