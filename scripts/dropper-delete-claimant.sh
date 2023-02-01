#!/usr/bin/env sh

curl \
    -X DELETE \
    localhost:7191/drops/claimants \
    -H "Authorization: moonstream $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"dropper_claim_id\": \"$DROPPER_CLAIM_ID\", \"addresses\": [\"$CLAIMANT_TO_REMOVE\"]}"
