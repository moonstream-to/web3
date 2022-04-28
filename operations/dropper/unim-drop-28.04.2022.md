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
- [ ] `export CU_UNIM_ADDRESS="0x64060aB139Feaae7f06Ca4E63189D86aDEb51691"`

### Create Drop on contract common lootbox

- [x] Create claim erc20 token

```

lootbox dropper create-claim \
 --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --token-type $CLAIM_TYPE \
    --token-address $CU_UNIM_ADDRESS \
    --token-id 0 \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

- [x] `export UNIM_CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```
lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $UNIM_CLAIM_ID
```


## Set signer

- [x] Get signer public key:

```
export SIGNER_ADDRESS=<redacted>
```

### Set signer on pool common lootbox

- [x] Set signer for claim:

```
lootbox dropper set-signer-for-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --claim-id $UNIM_CLAIM_ID \
    --signer-arg $SIGNER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS
```

- [x] Verify:

```
lootbox dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $UNIM_CLAIM_ID
```


## Set claim URIs

### UNIM

```
UNIM_CLAIM_ID_URI=<Hmm probably not need>
```

```
lootbox dropper set-claim-uri \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --claim-id $UNIM_CLAIM_ID \
    --uri $UNIM_CLAIM_ID_URI
```

- [x] Verify

```
lootbox dropper claim-uri --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $UNIM_CLAIM_ID
```

## Engine-db cli

### create new contract

- [x] Verify: `lootbox engine-db dropper list-contracts -b $BLOCKCHAIN_NAME`

- [x] `export DROPPER_CONTRACT_ID=<redacted>`


```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "Crypto Unicorns: UNIM" \
    --description "Some amount of pretty rare unicorn milk." \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $UNIM_CLAIM_ID
```

lootbox engine-db dropper list-drops --dropper-contract-id $DROPPER_CONTRACT_ID

- [x] `export DB_UNIM_CLAIM_ID=<id of claim you just created>`


## Set claims to active

- [x] Set claim as active (in `psql`):

```bash
psql $ENGINE_DB_URI -c "UPDATE dropper_claims SET active = true WHERE id = '$DB_UNIM_CLAIM_ID';"
```



# Transfer unim to dropper contract
# 
```
unim erc20 mint --network matic --address $CU_UNIM_ADDRESS --sender $CU_OWNER --gas-price $GAS_PRICE --confirmations $CONFIRMATIONS --account $DROPPER_ADDRESS --amount <some amount>
```
