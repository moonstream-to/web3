# Checklist Founders Badge List 4.18

# set enviroment variable

- [ ] MOONSTREAM_CORS_ALLOWED_ORIGINS
- [ ] AWS_DEFAULT_REGION
- [ ] MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID
- [ ] MOONSTREAM_AWS_SIGNER_IMAGE_ID
- [ ] BROWNIE_NETWORK
- [ ] ENGINE_DB_URI
- [ ] `export BROWNIE_NETWORK=<network name>`
- [ ] `export CLAIM_TYPE=1`
- [ ] `export SENDER=<keystore path>`
- [ ] `export SENDER_ADDRESS=$(jq -r .address $SENDER)`
- [ ] `export GAS_PRICE="<n> gwei"`
- [ ] `export CONFIRMATIONS=<m>`
- [ ] `export MAX_UINT=$(python -c "print(2**256 - 1)")`
- [ ] `export MAX_BADGES=<maximum number of badges that can exist>`
- [ ] `export ENGINE_API_URL=<api url for Engine API>`
- [ ] `export BLOCKCHAIN_NAME="polygon"`

# Deploy Dropper contract

```
lootbox dropper deploy --network $BROWNIE_NETWORK --sender $SENDER --confirmations $CONFIRMATIONS --gas-price "$GAS_PRICE"
```

- [x] `export DROPPER_ADDRESS="<address of deployed contract>"`


# Create terminus batch pool if not created yeat

- [ ] `export TERMINUS_ADDRESS="<address of Terminus contract on which we will create a badge>"`

- [ ] `export PAYMENT_TOKEN_ADDRESS="<address of ERC20 token used to pay for Terminus pool creation>"`

- [ ] Approve Terminus contract to spend payment token on your behalf:

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

- [ ] Create pool for badge
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

- [ ] `export BADGE_POOL_ID=$(lootbox terminus total-pools --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS)`

## move control of pool to dropper contract

- [ ] Transfer control

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

- [ ] Verify

```
lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id $BADGE_POOL_ID
```

# Create Drop on contract

- [ ] Create claim

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

- [ ] `export CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [ ] Verify

```
lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $CLAIM_ID
```

## Set signer

- [ ] `export SIGNING_SERVER_URL=<url of running signing server - https://github.com/bugout-dev/signer>`

- [ ] Get signer public key:

```
export SIGNER_ADDRESS=$(curl $SIGNING_SERVER_URL/pubkey | jq -r .pubkey)
```

- [ ] Set signer for claim:

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

- [ ] Verify:

```
lootbox dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $CLAIM_ID
```

# Engine-db cli

## create new contract

- [ ] Create row:
```
lootbox engine-db dropper create-contract -b $BLOCKCHAIN_NAME -a $DROPPER_ADDRESS

```

- [ ] Verify: `lootbox engine-db dropper list-contracts -b $BLOCKCHAIN_NAME`

- [ ] `export DROPPER_CONTRACT_ID=<primary key id for contract>`

## Create new drop

- [ ] Create title for drop: `export DROP_TITLE="Any title"`

- [ ] Create description for drop: `export DROP_DESCRIPTION="Any description"`

- [ ] Set block deadline: `export BLOCK_DEADLINE=<whatever>`

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_TITLE" \
    --description "$DROP_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $TERMINUS_ADDRESS \
    --terminus-pool-id $BADGE_POOL_ID \
    --claim-id $CLAIM_ID

```

- [ ] List drops:

```
lootbox engine-db dropper list-drops \
    --dropper-contract-id $DROPPER_CONTRACT_ID \
    -a false
```

- [ ] `export DB_CLAIM_ID=<id of claim you just created>`



## Add claimants to drop

- [ ] `export CLAIM_WHITELIST=<path to CSV file containing whitelist>`

```
lootbox engine-db dropper add-claimants \
    --dropper-claim-id $DB_CLAIM_ID \
    --claimants-file $CLAIM_WHITELIST

```

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
