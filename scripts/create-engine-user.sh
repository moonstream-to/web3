#!/usr/bin/env sh

BUGOUT_BROOD_URL=${BUGOUT_BROOD_URL:-https://auth.bugout.dev}

set -eu

curl -X POST "$BUGOUT_BROOD_URL/user" \
    -F "application_id=$MOONSTREAM_ENGINE_APPLICATION_ID" \
    -F "username=$MOONSTREAM_ENGINE_USERNAME" \
    -F "email=$MOONSTREAM_ENGINE_EMAIL" \
    -F "password=$MOONSTREAM_ENGINE_PASSWORD"
