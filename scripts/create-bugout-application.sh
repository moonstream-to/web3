#!/usr/bin/env sh

BUGOUT_BROOD_URL=${BUGOUT_BROOD_URL:-https://auth.bugout.dev}
APPLICATION_NAME=${MOONSTREAM_ENGINE_APPLICATION_NAME:-moonstream-engine}

set -eu

curl -X POST "$BUGOUT_BROOD_URL/applications" \
    -H "Authorization: Bearer $MOONSTREAM_ENGINE_ADMIN_ACCESS_TOKEN" \
    -F "group_id=$MOONSTREAM_ENGINE_GROUP_ID" \
    -F "name=$APPLICATION_NAME"
