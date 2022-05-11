# Checklist Golden Ticket List 5-5

# set enviroment variable

- [x] `export BROWNIE_NETWORK=<network name>`
- [x] `export CLAIM_TYPE=1`
- [x] `export SENDER=<keystore path>`
- [x] `export SENDER_ADDRESS=$(jq -r .address $SENDER)`
- [x] `export GAS_PRICE="250 gwei"`
- [x] `export CONFIRMATIONS=5`
- [x] `export MAX_UINT=$(python -c "print(2**256 - 1)")`
- [x] `export MAX_BADGES=$MAX_UINT`
- [x] `export ENGINE_API_URL=https://dropper.moonstream.to`
- [x] `export BLOCKCHAIN_NAME="polygon"`
- [x] `export DROPPER_ADDRESS="0x6bc613A25aFe159b70610b64783cA51C9258b92e"`


# Create terminus batch pool if not created yeat

- [x] `export TERMINUS_ADDRESS="0x99a558bdbde247c2b2716f0d4cfb0e246dfb697d"`

- [x] `export PAYMENT_TOKEN_ADDRESS="0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"`


- [x] Create pool for Golden Tickets
```
lootbox terminus create-pool-v1 \
    --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --capacity-arg $MAX_BADGES \
    --transferable-arg true \
    --burnable-arg true \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export GOLDEN_TICKET_POOL_ID=$(lootbox terminus total-pools --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS)`

- [x] Set metadata for Golden Tickets:

```
lootbox terminus set-uri \
    --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --pool-id $GOLDEN_TICKET_POOL_ID \
    --pool-uri 'https://badges.moonstream.to/golden-tickets/metadata.json'

```

- [x] Verify:

```
lootbox terminus uri \
    --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --pool-id $GOLDEN_TICKET_POOL_ID

```

## move control of pool to dropper contract

- [x] Transfer control

```
lootbox terminus set-pool-controller \
    --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $GOLDEN_TICKET_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Verify

```
lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id $GOLDEN_TICKET_POOL_ID
```

# Create Drop on contract

- [x] Create claim

```
lootbox dropper create-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER --token-type $CLAIM_TYPE \
    --token-address $TERMINUS_ADDRESS \
    --token-id $GOLDEN_TICKET_POOL_ID \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```
lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $CLAIM_ID
```

- [x] Set claim metadata

```
lootbox dropper set-claim-uri \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --claim-id $CLAIM_ID \
    --uri 'https://badges.moonstream.to/golden-tickets/metadata.json'

```

- [x] Verify: `lootbox dropper claim-uri --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $CLAIM_ID`

## Set signer

- [x] Set signer public key:

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

- [x] `lootbox engine-db dropper list-contracts -b $BLOCKCHAIN_NAME`

- [x] `export DROPPER_CONTRACT_ID=<primary key id for contract>`

## Create new drop

- [x] Create title for drop: `export DROP_TITLE="Any title"`

- [x] Create description for drop: `export DROP_DESCRIPTION="Any description"`

- [x] `export ADMIN_TERMINUS_ADDRESS="0x062BEc5e84289Da2CD6147E0e4DA402B33B8f796"`

- [x] `export ADMIN_POOL_ID="10"`

- [x] Set block deadline: `export BLOCK_DEADLINE=<whatever>`

- [x] Create drop

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_TITLE" \
    --description "$DROP_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $ADMIN_TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $CLAIM_ID

```

- [x] `export DB_CLAIM_ID=<id of claim you just created>`


## Set claim to active

- [ ] Set claim as active (in `psql`):

```bash
psql $ENGINE_DB_URI -c "UPDATE dropper_claims SET active = true WHERE id = '$DB_CLAIM_ID';"
```

# Get claim signature

- [ ] Address that you would like to get claim for: `export CLAIMANT_ADDRESS=<address>`

```
API_CALL=$(curl -X GET "$ENGINE_API_URL/drops?dropper_claim_id=$DB_CLAIM_ID&address=$CLAIMANT_ADDRESS")
```

- [ ] Set variables
```
signature=$(echo $API_CALL | jq -r '.signature') \
    block_deadline=$(echo $API_CALL | jq -r '.block_deadline') \
    amount=$(echo $API_CALL | jq -r '.amount') \
    claim_id=$(echo $API_CALL | jq -r '.claim_id') \
    claimant=$(echo $API_CALL | jq -r '.claimant')
```

# claim drop

```
lootbox dropper claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --claim-id $CLAIM_ID \
    --signature $signature \
    --block-deadline $block_deadline \
    --amount $amount

```
