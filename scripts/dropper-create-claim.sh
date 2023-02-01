#!/usr/bin/env sh

curl \
    -X POST \
    localhost:7191/drops/claims \
    -H "Authorization: moonstream $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"dropper_contract_id\": \"$DROPPER_CONTRACT_ID\", \"title\": \"Test claim\", \"description\": \"Test claim\"}"
