#!/usr/bin/env sh

# Compile application and run with provided arguments
set -e

PROGRAM_NAME="signer-ui_dev"

go build -o "$PROGRAM_NAME" cmd/ui/main.go

./"$PROGRAM_NAME" "$@"
