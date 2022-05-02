# enviroment variables

```
- [x] MOONSTREAM_CORS_ALLOWED_ORIGINS
- [x] AWS_DEFAULT_REGION
- [x] MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID
- [x] MOONSTREAM_AWS_SIGNER_IMAGE_ID
- [x] `export ENGINE_DB_URI=""`
- [x] `export BROWNIE_NETWORK=polygon-main`
- [x] `export TERMINUS_ADDRESS="0x062BEc5e84289Da2CD6147E0e4DA402B33B8f796"`
- [x] `export SENDER=<keystore path>`
- [x] `export SENDER_ADDRESS=$(jq -r .address $SENDER)`
- [x] `export CONFIRMATIONS=5`
- [x] `export GAS_PRICE="80 gwei"`
- [x] `export CLAIM_TYPE=1`
- [x] `export DARK_FOREST_ADDRESS=0x8d528e98A69FE27b11bb02Ac264516c4818C3942`
- [x] `export CU_TERMINUS_ADDRESS=0x99A558BDBdE247C2B2716f0D4cFb0E246DFB697D`
```

## Deploy Dropper contract on mainnet

```
lootbox dropper deploy --network $BROWNIE_NETWORK --sender $SENDER --gas-price "$GAS_PRICE" --confirmations $CONFIRMATIONS
```

- [x] `export DROPPER_ADDRESS="0x6bc613A25aFe159b70610b64783cA51C9258b92e"`

## Get pool ids of lootboxes

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

- [x] `export CU_TERMINUS_COMMON_LOOTBOX_POOL_ID="4"`
- [x] `export CU_TERMINUS_RARE_LOOTBOX_POOL_ID="5"`
- [x] `export CU_TERMINUS_MYTHIC_LOOTBOX_POOL_ID="6"`

Return pool control to owner of DarkForest contract lootboxes and eggs in one moment

```

wisp dark-forest surrender-terminus-pools --network $BROWNIE_NETWORK --address $DARK_FOREST_ADDRESS --sender $SENDER --gas-price "$GAS_PRICE" --confirmations $CONFIRMATIONS

```

### Check pool controller

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id 1
lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id 2
lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id 3
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


## Transfer pool control to dropper contract

### move control of pool to dropper contract

- [x] Transfer control of pool 4 to dropper contract

```

lootbox terminus set-pool-controller \
 --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $CU_TERMINUS_COMMON_LOOTBOX_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

- [x] Transfer control of pool 5 to dropper contract

```

lootbox terminus set-pool-controller \
 --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $CU_TERMINUS_RARE_LOOTBOX_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

- [x] Transfer control of pool 6 to dropper contract

```

lootbox terminus set-pool-controller \
 --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $CU_TERMINUS_MYTHIC_LOOTBOX_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

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

- [x] Verify:

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

- [x] Create row:

```
lootbox engine-db dropper create-contract -b polygon \
                                          -a $DROPPER_ADDRESS \
                                          -t "Dropper contract version 1" \
                                          -d "Crypto Unicorns Dropper contract" \
                                          -i "https://badges.moonstream.to/laguna-game-designers/laguna.png"
```

- [x] Verify: `lootbox engine-db dropper list-contracts -b $BLOCKCHAIN_NAME`

- [x] `export DROPPER_CONTRACT_ID=<redacted>`

### Create Laguna Games Game Designers Terminus pool (admin pool for claims)

- [x] Create Terminus pool

- [x] `export ADMIN_POOL_ID=$(lootbox terminus total-pools --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS)`

- [x] `export ADMIN_POOL_METADATA=https://badges.moonstream.to/laguna-game-designers/metadata.json`

- [x]

```
lootbox terminus set-uri \
    --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --pool-id $ADMIN_POOL_ID \
    --pool-uri $ADMIN_POOL_METADATA
```

- [x] Verify

```
lootbox terminus uri --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id $ADMIN_POOL_ID
```

### Create new drops

- [x]

```
export DROP_COMMON_LOOTBOX_TITLE="Crypto Unicorns: Common lootbox drop"
export DROP_COMMON_LOOTBOX_DESCRIPTION="Crypto Unicorns: Common lootbox drop of 2022-04-27"
export DROP_RARE_LOOTBOX_TITLE="Crypto Unicorns: Rare lootbox drop"
export DROP_RARE_LOOTBOX_DESCRIPTION="Crypto Unicorns: Rare lootbox drop of 2022-04-27"
export DROP_MYTHIC_LOOTBOX_TITLE="Crypto Unicorns: Mythic lootbox drop"
export DROP_MYTHIC_LOOTBOX_DESCRIPTION="Crypto Unicorns: Mythic lootbox drop of 2022-04-27"
```

- [x] Set block deadline: `export BLOCK_DEADLINE=27644242`

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_COMMON_LOOTBOX_TITLE" \
    --description "$DROP_COMMON_LOOTBOX_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $COMMON_LOOTBOX_CLAIM_ID

```

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_RARE_LOOTBOX_TITLE" \
    --description "$DROP_RARE_LOOTBOX_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $RARE_LOOTBOX_CLAIM_ID

```

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_MYTHIC_LOOTBOX_TITLE" \
    --description "$DROP_MYTHIC_LOOTBOX_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $MYTHIC_LOOTBOX_CLAIM_ID

```

- [x] `export DB_COMMON_LOOTBOX_CLAIM_ID=<id of claim you just created>`
- [x] `export DB_RARE_LOOTBOX_CLAIM_ID=<id of claim you just created>`
- [x] `export DB_MYTHIC_LOOTBOX_CLAIM_ID=<id of claim you just created>`

## Set claims to active

- [x] Set claim as active (in `psql`):

```bash
psql $ENGINE_DB_URI -c "UPDATE dropper_claims SET active = true WHERE id in ('$DB_COMMON_LOOTBOX_CLAIM_ID','$DB_RARE_LOOTBOX_CLAIM_ID','$DB_MYTHIC_LOOTBOX_CLAIM_ID');"
```
