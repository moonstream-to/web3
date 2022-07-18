#!/usr/bin/env sh

# Compile application and run with provided arguments
set -e

PROGRAM_NAME="signer_dev"

go build -o "$PROGRAM_NAME" cmd/signer/*.go

./"$PROGRAM_NAME" "$@"
