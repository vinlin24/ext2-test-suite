#!/usr/bin/env bash
# Script to automate setting up the test suite in your lab4 directory.

# USAGE: ./setup.sh /path/to/lab4

if [ $# -eq 0 ]; then
    echo >&2 "$0: Specify the directory to set up in."
    echo >&2 "USAGE: $0 /path/to/lab4"
    exit 1
fi

lab_dir="$1"

if [ ! -d "$lab_dir" ]; then
    echo >&2 "$0: ${lab_dir} is not a valid directory path."
    exit 1
fi

# Overengineering be like.
tarball_name=$(sed -En 's/suite: (.+)$/\1/p' Makefile)
suite_files=$(sed -En 's/SUITE_FILES = (.+)/\1/p' Makefile | tr ' ' '\n')

ignore_additions="\n# Test suite\n*.tar\n${suite_files}\n"

# Their .gitignore has already set up this test suite before.
if grep -q '# Test suite' "${lab_dir}/.gitignore" 2>/dev/null; then
    ignore_additions=""
fi

# A trick to seeing if any command in a sequence exited with error.
err=0
trap 'err=1' ERR

# Actual setup sequence.
make suite
cp "$tarball_name" "$lab_dir"
cd "$lab_dir"
tar -xf "$tarball_name"
rm "$tarball_name"
echo -en "$ignore_additions" >>.gitignore

# Check if any of the commands exited with error.

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
END=$(tput sgr0)

if [ $err -eq 0 ]; then
    echo -n "${GREEN}The lab suite has been set up in ${lab_dir}. "
    echo "Happy coding!${END}"
else
    echo >&2 "${RED}Something went wrong, setup might be incomplete.${END}"
    exit 1
fi
