- [x] `export BROWNIE_NETWORK=polygon-main`
- [x] `export CLAIM_TYPE=20`
- [x] `export SENDER=<keystore path>`
- [x] `export SENDER_ADDRESS=$(jq -r .address $SENDER)`
- [x] `export GAS_PRICE="350 gwei"`
- [x] `export CONFIRMATIONS=5`
- [x] `export MAX_UINT=$(python -c "print(2**256 - 1)")`
- [x] `export ENGINE_API_URL=<api url for Engine API>`
- [x] `export BLOCKCHAIN_NAME="polygon"`
- [x] `export DROPPER_ADDRESS="0x6bc613A25aFe159b70610b64783cA51C9258b92e"`
- [x] `export CU_UNIM_ADDRESS="0x64060aB139Feaae7f06Ca4E63189D86aDEb51691"`
- [x] `export ADMIN_TERMINUS_ADDRESS="0x062BEc5e84289Da2CD6147E0e4DA402B33B8f796"`
- [x] `export ADMIN_POOL_ID=10`

### Create Drop on UNIM

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
export SIGNER_ADDRESS=0x127078127f6067AAA7a762E2EF5c8217cbeCECE4
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
UNIM_CLAIM_URI="https://badges.moonstream.to/cu-erc20-tokens/unim.json"
```

```
lootbox dropper set-claim-uri \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --claim-id $UNIM_CLAIM_ID \
    --uri $UNIM_CLAIM_URI
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
    --title "UNIM Token (April Staking Rewards - May 13, 2022)" \
    --description "Unicorn Milk (UNIM) is used to breed and evolve Unicorns as well as craft high-value items and boosters." \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $ADMIN_TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $UNIM_CLAIM_ID
```
