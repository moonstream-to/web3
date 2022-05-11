# enviroment variables

```
- [x] `export BROWNIE_NETWORK=polygon-main`
- [x] `export TERMINUS_ADDRESS="0x062BEc5e84289Da2CD6147E0e4DA402B33B8f796"`
- [x] `export SENDER=<keystore path>`
- [x] `export SENDER_ADDRESS=$(jq -r .address $SENDER)`
- [x] `export CONFIRMATIONS=5`
- [x] `export GAS_PRICE="150 gwei"`
- [x] `export CLAIM_TYPE=1`
- [x] `export CU_TERMINUS_ADDRESS=0x99A558BDBdE247C2B2716f0D4cFb0E246DFB697D`
```

## Set up badges

### Upload images and metadata to https://badges.moonstream.to

- [x] Tier 1: https://badges.moonstream.to/shadowcorn-act-1-badges/tier-1.json

- [x] Tier 2: https://badges.moonstream.to/shadowcorn-act-1-badges/tier-2.json

- [x] Tier 3: https://badges.moonstream.to/shadowcorn-act-1-badges/tier-3.json

## Create Terminus pools

- [x] Tier 1 creation

```
lootbox terminus create-pool-v1 \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --capacity-arg $MAX_BADGES \
    --transferable-arg false \
    --burnable-arg true \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export TIER_1_POOL_ID=$(lootbox terminus total-pools --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS)`

- [x] Tier 2

```
lootbox terminus create-pool-v1 \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --capacity-arg $MAX_BADGES \
    --transferable-arg false \
    --burnable-arg true \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export TIER_2_POOL_ID=$(lootbox terminus total-pools --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS)`

- [x] Tier 3

```
lootbox terminus create-pool-v1 \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --capacity-arg $MAX_BADGES \
    --transferable-arg false \
    --burnable-arg true \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export TIER_3_POOL_ID=$(lootbox terminus total-pools --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS)`

## Set Terminus metadata

- [x] Tier 1 badge

```
lootbox terminus set-uri \
    --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --pool-id $TIER_1_POOL_ID \
    --pool-uri 'https://badges.moonstream.to/shadowcorn-act-1-badges/tier-1.json'

```

- [x] Verify Tier 1 badge metadata

```
curl -L --max-redirs 4 -X GET $(lootbox terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_1_POOL_ID)
```

- [x] Tier 2 badge

```
lootbox terminus set-uri \
    --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --pool-id $TIER_2_POOL_ID \
    --pool-uri 'https://badges.moonstream.to/shadowcorn-act-1-badges/tier-2.json'

```

- [x] Verify Tier 2 badge metadata

```
curl -L --max-redirs 4 -X GET $(lootbox terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_2_POOL_ID)
```

- [x] Tier 3 badge

```
lootbox terminus set-uri \
    --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --pool-id $TIER_3_POOL_ID \
    --pool-uri 'https://badges.moonstream.to/shadowcorn-act-1-badges/tier-3.json'

```

- [x] Verify Tier 3 badge metadata

```
curl -L --max-redirs 4 -X GET $(lootbox terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_3_POOL_ID)
```


### Transfer pool control to Dropper contract

- [x] Tier 1 badge

```
lootbox terminus set-pool-controller \
    --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $TIER_1_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Tier 2 badge

```
lootbox terminus set-pool-controller \
    --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $TIER_2_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Tier 3 badge

```
lootbox terminus set-pool-controller \
    --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $TIER_3_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Verify
```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_1_POOL_ID
lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_2_POOL_ID
lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_3_POOL_ID

```

### Create claims on Dropper contract

- [x] Tier 1

```

lootbox dropper create-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --token-type $CLAIM_TYPE \
    --token-address $CU_TERMINUS_ADDRESS \
    --token-id $TIER_1_POOL_ID \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export TIER_1_CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```

lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_1_CLAIM_ID

```

- [x] Tier 2

```

lootbox dropper create-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --token-type $CLAIM_TYPE \
    --token-address $CU_TERMINUS_ADDRESS \
    --token-id $TIER_2_POOL_ID \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export TIER_2_CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```

lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_2_CLAIM_ID

```

- [x] Tier 3

```

lootbox dropper create-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --token-type $CLAIM_TYPE \
    --token-address $CU_TERMINUS_ADDRESS \
    --token-id $TIER_3_POOL_ID \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export TIER_3_CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```

lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_3_CLAIM_ID

```

## Verify that Dropper contract is pool controller for lootbox pools

- [x] Verify

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_1_POOL_ID

```

- [x] Verify

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_2_POOL_ID

```

- [x] Verify

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_3_POOL_ID

```


## Set signer

- [x] Get signer public key:

```
export SIGNER_ADDRESS=<redacted>
```

- [x] Tier 1

```
lootbox dropper set-signer-for-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --claim-id $TIER_1_CLAIM_ID \
    --signer-arg $SIGNER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Verify:

```
lootbox dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_1_CLAIM_ID
```

- [x] Tier 2

```
lootbox dropper set-signer-for-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --claim-id $TIER_2_CLAIM_ID \
    --signer-arg $SIGNER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Verify:

```
lootbox dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_2_CLAIM_ID
```

- [x] Tier 3

```
lootbox dropper set-signer-for-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --claim-id $TIER_3_CLAIM_ID \
    --signer-arg $SIGNER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Verify:

```
lootbox dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_3_CLAIM_ID
```

## Set claim URIs

### Tier 1

- [x] Get metadata from Terminus:

```
TIER_1_URI=$(lootbox terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_1_POOL_ID)
```

- [x] Set claim URI

```
lootbox dropper set-claim-uri \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --claim-id $TIER_1_CLAIM_ID \
    --uri $TIER_1_URI
```

- [x] Verify

```
lootbox dropper claim-uri --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_1_CLAIM_ID
```

### Tier 2

- [x] Get metadata from Terminus:

```
TIER_2_URI=$(lootbox terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_2_POOL_ID)
```

- [x] Set claim URI

```
lootbox dropper set-claim-uri \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --claim-id $TIER_2_CLAIM_ID \
    --uri $TIER_2_URI
```

- [x] Verify

```
lootbox dropper claim-uri --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_2_CLAIM_ID
```

### Tier 3

- [x] Get metadata from Terminus:

```
TIER_3_URI=$(lootbox terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_3_POOL_ID)
```

- [x] Set claim URI

```
lootbox dropper set-claim-uri \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --claim-id $TIER_3_CLAIM_ID \
    --uri $TIER_3_URI
```

- [x] Verify

```
lootbox dropper claim-uri --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_3_CLAIM_ID
```


## Engine-db cli

### create new contract

- [x] Verify: `lootbox engine-db dropper list-contracts -b $BLOCKCHAIN_NAME`

- [x] `export DROPPER_CONTRACT_ID=<redacted>`

- [x] `export ADMIN_TERMINUS_ADDRESS="0x062BEc5e84289Da2CD6147E0e4DA402B33B8f796"`
- [x] `export ADMIN_POOL_ID=10`


### Create new drops

- [x]

```
export DROP_TIER_1_TITLE="Shadowcorn Act I Tier I Badge"
export DROP_TIER_1_DESCRIPTION="Shadowcorn Act I Tier I Badge"
export DROP_TIER_2_TITLE="Shadowcorn Act I Tier II Badge"
export DROP_TIER_2_DESCRIPTION="Shadowcorn Act I Tier II Badge"
export DROP_TIER_3_TITLE="Shadowcorn Act I Tier III Badge"
export DROP_TIER_3_DESCRIPTION="Shadowcorn Act I Tier III Badge"
```

- [x] Set block deadline: `export BLOCK_DEADLINE=29000000`

- [x] Tier 1
```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_TIER_1_TITLE" \
    --description "$DROP_TIER_1_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $ADMIN_TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $TIER_1_CLAIM_ID

```

- [x] Tier 2
```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_TIER_2_TITLE" \
    --description "$DROP_TIER_2_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $ADMIN_TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $TIER_2_CLAIM_ID

```

- [x] Tier 3
```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_TIER_3_TITLE" \
    --description "$DROP_TIER_3_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $ADMIN_TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $TIER_3_CLAIM_ID

```

- [x] `export DB_TIER_1_CLAIM_ID=<id of claim you just created>`
- [x] `export DB_TIER_2_CLAIM_ID=<id of claim you just created>`
- [x] `export DB_TIER_3_CLAIM_ID=<id of claim you just created>`

## Set claims to active

- [ ] Set claim as active (in `psql`):

```bash
psql $ENGINE_DB_URI -c "UPDATE dropper_claims SET active = true WHERE id in ('$DB_TIER_1_CLAIM_ID','$DB_TIER_2_CLAIM_ID','$DB_TIER_3_CLAIM_ID');"
```
