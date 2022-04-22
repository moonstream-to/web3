# Checklist Founders Badge List 4.18

# set enviroment variable

- [x] MOONSTREAM_CORS_ALLOWED_ORIGINS
- [x] AWS_DEFAULT_REGION
- [x] MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID
- [x] MOONSTREAM_AWS_SIGNER_IMAGE_ID
- [x] BROWNIE_NETWORK
- [x] ENGINE_DB_URI
- [x] `export BROWNIE_NETWORK=<network name>`
- [x] `export CLAIM_TYPE=1`
- [x] `export SENDER=<keystore path>`
- [x] `export SENDER_ADDRESS=$(jq -r .address $SENDER)`
- [x] `export GAS_PRICE="<n> gwei"`
- [x] `export CONFIRMATIONS=<m>`
- [x] `export MAX_UINT=$(python -c "print(2**256 - 1)")`
- [x] `export MAX_BADGES=$MAX_UINT`
- [x] `export ENGINE_API_URL=<api url for Engine API>`
- [x] `export BLOCKCHAIN_NAME="polygon"`

# Deploy Dropper contract

- [x] `export DROPPER_ADDRESS="0x7bbf900Ded826D5A16a27dF028018673E521B35d"`


# Create terminus batch pool if not created yeat

- [x] `export TERMINUS_ADDRESS="0x99A558BDBdE247C2B2716f0D4cFb0E246DFB697D"`

- [x] `export PAYMENT_TOKEN_ADDRESS="0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"`

- [x] Approve Terminus contract to spend payment token on your behalf:

```
lootbox mock-erc20 approve \
    --network $BROWNIE_NETWORK \
    --address $PAYMENT_TOKEN_ADDRESS \
    --sender $SENDER \
    --spender $TERMINUS_ADDRESS \
    --amount $MAX_UINT \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS
```

- [x] Create pool for badge
```
lootbox terminus create-pool-v1 \
    --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --capacity-arg $MAX_BADGES \
    --transferable-arg false \
    --burnable-arg true \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export BADGE_POOL_ID=$(lootbox terminus total-pools --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS)`

## move control of pool to dropper contract

- [x] Transfer control

```
lootbox terminus set-pool-controller \
    --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $BADGE_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Verify

```
lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id $BADGE_POOL_ID
```

# Create Drop on contract

- [x] Create claim

```
lootbox dropper create-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER --token-type $CLAIM_TYPE \
    --token-address $TERMINUS_ADDRESS \
    --token-id $BADGE_POOL_ID \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```
lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $CLAIM_ID
```

Output:
```
(1, '0x99A558BDBdE247C2B2716f0D4cFb0E246DFB697D', 41, 1)
```

## Set signer

- [x] Get signer public key:

```
export SIGNER_ADDRESS=<redacted>
```

- [x] Set signer for claim:

```
lootbox dropper set-signer-for-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --claim-id $CLAIM_ID \
    --signer-arg $SIGNER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Verify:

```
lootbox dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $CLAIM_ID
```

# Engine-db cli

## create new contract

- [x] Verify: `lootbox engine-db dropper list-contracts -b $BLOCKCHAIN_NAME`

- [x] `export DROPPER_CONTRACT_ID=<primary key id for contract>`

## Create new drop

- [x] Create title for drop: `export DROP_TITLE="Founders Badge"`

- [x] Create description for drop: `export DROP_DESCRIPTION="Crypto Unicorns Founders Badge"`

- [x] Set block deadline: `export BLOCK_DEADLINE=<whatever>`

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_TITLE" \
    --description "$DROP_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $TERMINUS_ADDRESS \
    --terminus-pool-id $BADGE_POOL_ID \
    --claim-id $CLAIM_ID

```

- [x] List drops:

```
lootbox engine-db dropper list-drops \
    --dropper-contract-id $DROPPER_CONTRACT_ID \
    -a false
```

- [x] `export DB_CLAIM_ID=<id of claim you just created>`



## Add claimants to drop

- [x] `export CLAIM_WHITELIST=<path to CSV file containing whitelist>`

```
lootbox engine-db dropper add-claimants \
    --dropper-claim-id $DB_CLAIM_ID \
    --claimants-file $CLAIM_WHITELIST

```

## Set claim to active

- [x] Set claim as active (in `psql`):

```bash
psql $ENGINE_DB_URI -c "UPDATE dropper_claims SET active = true WHERE id = '$DB_CLAIM_ID';"
```
