# enviroment variables

```
- [x] `export BROWNIE_NETWORK=polygon-main`
- [x] `export TERMINUS_ADDRESS="0x062BEc5e84289Da2CD6147E0e4DA402B33B8f796"`
- [x] `export SENDER=<keystore path>`
- [x] `export SENDER_ADDRESS=$(jq -r .address $SENDER)`
- [x] `export CONFIRMATIONS=5`
- [x] `export GAS_PRICE="80 gwei"`
- [x] `export CLAIM_TYPE=1`
- [x] `export CU_TERMINUS_ADDRESS=0x99A558BDBdE247C2B2716f0D4cFb0E246DFB697D`
```

## Deploy Dropper contract on mainnet

4, 5, 6

Check pool uri

### Common

```
curl -L --max-redirs 4 -X GET $(lootbox terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id 4)
```

### Rare

```
curl -L --max-redirs 4 -X GET $(lootbox terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id 5)
```

### Mythical

```

curl -L --max-redirs 4 -X GET $(lootbox terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id 6)

```

- [x]

```
export CU_TERMINUS_COMMON_LOOTBOX_POOL_ID="4"
export CU_TERMINUS_RARE_LOOTBOX_POOL_ID="5"
export CU_TERMINUS_MYTHIC_LOOTBOX_POOL_ID="6"
```

### Check pool controller

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id 4
lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id 5
lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id 6

```

### Create Drop on contract common lootbox

- [x] Create claim common lootbox

```

lootbox dropper create-claim \
 --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --token-type $CLAIM_TYPE \
    --token-address $CU_TERMINUS_ADDRESS \
    --token-id $CU_TERMINUS_COMMON_LOOTBOX_POOL_ID \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

- [x] `export COMMON_LOOTBOX_CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```

lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $COMMON_LOOTBOX_CLAIM_ID

```

### Create Drop on contract rare lootbox

- [x] Create claim rare lootbox

```

lootbox dropper create-claim \
 --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --token-type $CLAIM_TYPE \
    --token-address $CU_TERMINUS_ADDRESS \
    --token-id $CU_TERMINUS_RARE_LOOTBOX_POOL_ID \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

- [x] `export RARE_LOOTBOX_CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```

lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $RARE_LOOTBOX_CLAIM_ID

```

### Create Drop on contract myth lootbox

- [x] Create claim myth lootbox

```

lootbox dropper create-claim \
 --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --token-type $CLAIM_TYPE \
    --token-address $CU_TERMINUS_ADDRESS \
    --token-id $CU_TERMINUS_MYTHIC_LOOTBOX_POOL_ID \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

- [x] `export MYTHIC_LOOTBOX_CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```

lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $MYTHIC_LOOTBOX_CLAIM_ID

```


## Verify that Dropper contract is pool controller for lootbox pools

- [x] Verify

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $CU_TERMINUS_COMMON_LOOTBOX_POOL_ID

```

- [x] Verify

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $CU_TERMINUS_RARE_LOOTBOX_POOL_ID

```

- [x] Verify

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $CU_TERMINUS_MYTHIC_LOOTBOX_POOL_ID

```


## Set signer

- [ ] Get signer public key:

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
    --claim-id $COMMON_LOOTBOX_CLAIM_ID \
    --signer-arg $SIGNER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Verify:

```
lootbox dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $COMMON_LOOTBOX_CLAIM_ID
```

### Set signer on pool rare lootbox

- [x] Set signer for claim:

```
lootbox dropper set-signer-for-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --claim-id $RARE_LOOTBOX_CLAIM_ID \
    --signer-arg $SIGNER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Verify:

```
lootbox dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $RARE_LOOTBOX_CLAIM_ID
```

### Set signer on pool mythic lootbox

- [x] Set signer for claim:

```
lootbox dropper set-signer-for-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --claim-id $MYTHIC_LOOTBOX_CLAIM_ID \
    --signer-arg $SIGNER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [ ] Verify:

```
lootbox dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $MYTHIC_LOOTBOX_CLAIM_ID
```

## Set claim URIs

### Common

- [x] Get metadata from Terminus:

```
COMMON_LOOTBOX_URI=$(lootbox terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $CU_TERMINUS_COMMON_LOOTBOX_POOL_ID)
```

- [x] Set claim URI

```
lootbox dropper set-claim-uri \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --claim-id $COMMON_LOOTBOX_CLAIM_ID \
    --uri $COMMON_LOOTBOX_URI
```

- [x] Verify

```
lootbox dropper claim-uri --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $COMMON_LOOTBOX_CLAIM_ID
```

### Rare

- [x] Get metadata from Terminus:

```
RARE_LOOTBOX_URI=$(lootbox terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $CU_TERMINUS_RARE_LOOTBOX_POOL_ID)
```

- [x] Set claim URI

```
lootbox dropper set-claim-uri \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --claim-id $RARE_LOOTBOX_CLAIM_ID \
    --uri $RARE_LOOTBOX_URI
```

- [x] Verify

```
lootbox dropper claim-uri --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $RARE_LOOTBOX_CLAIM_ID
```

### Mythic

- [x] Get metadata from Terminus:

```
MYTHIC_LOOTBOX_URI=$(lootbox terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $CU_TERMINUS_MYTHIC_LOOTBOX_POOL_ID)
```

- [x] Set claim URI

```
lootbox dropper set-claim-uri \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --claim-id $MYTHIC_LOOTBOX_CLAIM_ID \
    --uri $MYTHIC_LOOTBOX_URI
```

- [x] Verify

```
lootbox dropper claim-uri --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $MYTHIC_LOOTBOX_CLAIM_ID
```


## Engine-db cli

### create new contract

- [x] Verify: `lootbox engine-db dropper list-contracts -b $BLOCKCHAIN_NAME`

- [x] `export DROPPER_CONTRACT_ID=<redacted>`

### Create Laguna Games Game Designers Terminus pool (admin pool for claims)

- [x] `export ADMIN_TERMINUS_ADDRESS="0x062BEc5e84289Da2CD6147E0e4DA402B33B8f796"`
- [x] `export ADMIN_POOL_ID=10`


### Create new drops

- [x]

```
export DROP_COMMON_LOOTBOX_TITLE="Crypto Unicorns: Common lootbox drop (Leaderboard)"
export DROP_COMMON_LOOTBOX_DESCRIPTION="Crypto Unicorns: Common lootbox drop of 2022-05-05"
export DROP_RARE_LOOTBOX_TITLE="Crypto Unicorns: Rare lootbox drop (Leaderboard)"
export DROP_RARE_LOOTBOX_DESCRIPTION="Crypto Unicorns: Rare lootbox drop of 2022-05-05"
export DROP_MYTHIC_LOOTBOX_TITLE="Crypto Unicorns: Mythic lootbox drop (Leaderboard)"
export DROP_MYTHIC_LOOTBOX_DESCRIPTION="Crypto Unicorns: Mythic lootbox drop of 2022-05-05"
```

- [x] Set block deadline: `export BLOCK_DEADLINE=29000000`

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_COMMON_LOOTBOX_TITLE" \
    --description "$DROP_COMMON_LOOTBOX_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $ADMIN_TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $COMMON_LOOTBOX_CLAIM_ID

```

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_RARE_LOOTBOX_TITLE" \
    --description "$DROP_RARE_LOOTBOX_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $ADMIN_TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $RARE_LOOTBOX_CLAIM_ID

```

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_MYTHIC_LOOTBOX_TITLE" \
    --description "$DROP_MYTHIC_LOOTBOX_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $ADMIN_TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $MYTHIC_LOOTBOX_CLAIM_ID

```

- [ ] `export DB_COMMON_LOOTBOX_CLAIM_ID=<id of claim you just created>`
- [ ] `export DB_RARE_LOOTBOX_CLAIM_ID=<id of claim you just created>`
- [ ] `export DB_MYTHIC_LOOTBOX_CLAIM_ID=<id of claim you just created>`

## Set claims to active

- [ ] Set claim as active (in `psql`):

```bash
psql $ENGINE_DB_URI -c "UPDATE dropper_claims SET active = true WHERE id in ('$DB_COMMON_LOOTBOX_CLAIM_ID','$DB_RARE_LOOTBOX_CLAIM_ID','$DB_MYTHIC_LOOTBOX_CLAIM_ID');"
```
