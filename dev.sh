#!/usr/bin/env sh

# Expects access to Python environment with the requirements 
# for this project installed.
set -e

LOOTBOX_PORT="${LOOTBOX_PORT:-7191}"

uvicorn --port "$LOOTBOX_PORT" --host 127.0.0.1 --workers 2 lootbox.api:app
