- [x] MOONSTREAM_CORS_ALLOWED_ORIGINS
- [x] AWS_DEFAULT_REGION
- [x] MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID
- [x] MOONSTREAM_AWS_SIGNER_IMAGE_ID
- [x] ENGINE_DB_URI
- [x] `export BROWNIE_NETWORK=polygon-main`
- [x] `export CLAIM_TYPE=20`
- [x] `export SENDER=<keystore path>`
- [x] `export SENDER_ADDRESS=$(jq -r .address $SENDER)`
- [x] `export GAS_PRICE="<n> gwei"`
- [x] `export CONFIRMATIONS=<m>`
- [x] `export MAX_UINT=$(python -c "print(2**256 - 1)")`
- [x] `export MAX_BADGES=<maximum number of badges that can exist>`
- [x] `export ENGINE_API_URL=<api url for Engine API>`
- [x] `export BLOCKCHAIN_NAME="polygon"`
- [ ] `export DROPPER_ADDRESS="0x6bc613A25aFe159b70610b64783cA51C9258b92e"`
- [ ] `export CU_RBW_ADDRESS="0x431CD3C9AC9Fc73644BF68bF5691f4B83F9E104f"`

### Create Drop on contract common lootbox

- [x] Create claim erc20 token

```

lootbox dropper create-claim \
 --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --token-type $CLAIM_TYPE \
    --token-address $CU_RBW_ADDRESS \
    --token-id 0 \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

- [x] `export RBW_CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```
lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $RBW_CLAIM_ID
```

## Set signer

- [ ] Get signer public key:

```
export SIGNER_ADDRESS=<redacted>
```

### Set signer on pool common lootbox

- [ ] Set signer for claim:

```
lootbox dropper set-signer-for-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --claim-id $RBW_CLAIM_ID \
    --signer-arg $SIGNER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS
```

- [ ] Verify:

```
lootbox dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $RBW_CLAIM_ID
```

## Set claim URIs

### UNIM

```
RBW_CLAIM_ID_URI=<Hmm probably not need>
```

```
lootbox dropper set-claim-uri \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --claim-id $RBW_CLAIM_ID \
    --uri $RBW_CLAIM_ID_URI
```

- [ ] Verify

```
lootbox dropper claim-uri --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $RBW_CLAIM_ID
```

## Engine-db cli

### create new contract

- [ ] Verify: `lootbox engine-db dropper list-contracts -b $BLOCKCHAIN_NAME`

- [ ] `export DROPPER_CONTRACT_ID=<redacted>`

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "Crypto Unicorns: Rainbow tokens." \
    --description "Some amount of pretty rare Rainbow tokens." \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $RBW_CLAIM_ID
```

lootbox engine-db dropper list-drops --dropper-contract-id $DROPPER_CONTRACT_ID

- [ ] `export DB_RBW_CLAIM_ID=<id of claim you just created>`

## Set claims to active

- [ ] Set claim as active (in `psql`):

```bash
psql $ENGINE_DB_URI -c "UPDATE dropper_claims SET active = true WHERE id = '$DB_RBW_CLAIM_ID';"
```

# Transfer unim to dropper contract

#

```
RBW erc20 mint --network matic --address $CU_RBW_ADDRESS --sender $CU_OWNER --gas-price $GAS_PRICE --confirmations $CONFIRMATIONS --account $DROPPER_ADDRESS --amount <some amount>
```
