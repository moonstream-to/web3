#!/usr/bin/env sh

# Expects access to Python environment with the requirements 
# for this project installed.
set -e

ENGINE_PORT="${ENGINE_PORT:-7191}"

uvicorn --port "$ENGINE_PORT" --host 127.0.0.1 --workers 2 engineapi.api:app
