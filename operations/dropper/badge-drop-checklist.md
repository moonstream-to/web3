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
    --transferable-arg False \
    --burnable-arg False \
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

```
lootbox engine-db dropper create-contract -b $BROWNIE_NETWORK -a $DROPPER_ADDRESS

```

## Lookup contract id

```
lootbox engine-db dropper list-contracts -b $BROWNIE_NETWORK
```

# set enviroment variable

- [ ] $DROPPER_CONTRACT_ID

## Create new drop

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
--title "cli-drop" \
--description "test" \
--block-deadline 29017888 \
--terminus-address $TERMINUS_ADDRESS \
--terminus-pool-id $BADGE_POOL_ID \
--claim-id $CLAIM_ID
```

## list drops

```
lootbox engine-db dropper list-drops \ --dropper-contract-id $DROPPER_CONTRACT_ID \
 -a false
```

# set enviroment variable

- [ ] $DROPPER_CLAIM_ID

## Add claimant to drop

```
lootbox engine-db dropper add-claimants \ --dropper-claim-id $DROPPER_CLAIM_ID \
 --claimants-file white-list.csv
```

# Get claim signature

```
API_CALL=$(curl -X GET "http://localhost:8000/drops?claim_id=<$CLAIM_ID>&address=<user_address>")
```

```
signature=$(echo $API_CALL | jq -r '.signature')
```

```
block_deadline=$(echo $API_CALL | jq -r '.block_deadline')
```

```
amount=$(echo $API_CALL | jq -r '.amount')
```

```
claim_id=$(echo $API_CALL | jq -r '.claim_id')
```

# claim drop

```
lootbox dropper claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --sender $SENDER --claim-id $CLAIM_ID --signature $signature --block-deadline $block_deadline --amount $amount
```
