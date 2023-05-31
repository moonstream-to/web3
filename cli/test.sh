#!/usr/bin/env sh

# Expects a Python environment to be active in which `dao` has been installed for development.
# You can set up the local copy of `dao` for development using:
# pip install -e .[dev]

set -e

GAS_PROFILE=${GAS_PROFILE:-n}

usage() {
    echo "Usage: $0" [TEST_SPEC ...]
    echo
    echo "Arguments:"
    echo "----------"
    echo "TEST_SPEC"
    echo "\tPython unittest specification of which test to run, following: https://docs.python.org/3/library/unittest.html#command-line-interface"
    echo "\tFor example: $0 lootbox.test_lootbox.TestLootbox"
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]
then
    usage
    exit 2
fi

TEST_COMMAND=${@:-discover}

cd ..
brownie compile
cd -
set -x
GAS_PROFILE="$GAS_PROFILE" python -m unittest $TEST_COMMAND 
