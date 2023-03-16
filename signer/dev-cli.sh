#!/usr/bin/env sh

# Compile application and run with provided arguments
set -e

PROGRAM_NAME="signer-cli_dev"

go build -o "$PROGRAM_NAME" cmd/cli/main.go

./"$PROGRAM_NAME" "$@"
