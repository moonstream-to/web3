# enviroment variables

```
- [x] `export BROWNIE_NETWORK=polygon-main`
- [x] `export SENDER=<keystore path>`
- [x] `export SENDER_ADDRESS=$(jq -r .address $SENDER)`
- [x] `export CONFIRMATIONS=5`
- [x] `export GAS_PRICE="100 gwei"`
- [x] `export CLAIM_TYPE=1`
- [x] `export CU_TERMINUS_ADDRESS=0x99A558BDBdE247C2B2716f0D4cFb0E246DFB697D`
- [x] `export ADMIN_TERMINUS_ADDRESS="0x062BEc5e84289Da2CD6147E0e4DA402B33B8f796"`
- [x] `export ADMIN_POOL_ID=10`
- [x] `export MAX_BADGES=$(python -c "print(2**256 - 1)")`
- [x] `export DROPPER_ADDRESS=0x6bc613A25aFe159b70610b64783cA51C9258b92e`
```

## Set up badges

### Upload images and metadata to https://badges.moonstream.to

- [x] Tier 1: https://badges.moonstream.to/cu-survival-badges/tier-1.json

- [x] Tier 2: https://badges.moonstream.to/cu-survival-badges/tier-2.json

- [x] Tier 3: https://badges.moonstream.to/cu-survival-badges/tier-3.json

- [x] Launch Badge: https://badges.moonstream.to/cu-launch-badge/metadata.json

## Create Terminus pools

- [ ] Tier 1 creation

```
engine terminus create-pool-v1 \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --capacity-arg $MAX_BADGES \
    --transferable-arg false \
    --burnable-arg true \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export TIER_1_POOL_ID=$(engine terminus total-pools --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS)`

(`47`)

- [ ] Tier 2

```
engine terminus create-pool-v1 \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --capacity-arg $MAX_BADGES \
    --transferable-arg false \
    --burnable-arg true \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export TIER_2_POOL_ID=$(engine terminus total-pools --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS)`

(`48`)

- [x] Tier 3

```
engine terminus create-pool-v1 \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --capacity-arg $MAX_BADGES \
    --transferable-arg false \
    --burnable-arg true \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export TIER_3_POOL_ID=$(engine terminus total-pools --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS)`

(`49`)

- [x] Launch badge

```
engine terminus create-pool-v1 \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --capacity-arg $MAX_BADGES \
    --transferable-arg false \
    --burnable-arg true \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export LAUNCH_BADGE_POOL_ID=$(engine terminus total-pools --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS)`

(`50`)


## Set Terminus metadata

- [x] Tier 1 badge

```
engine terminus set-uri \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --pool-id $TIER_1_POOL_ID \
    --pool-uri 'https://badges.moonstream.to/cu-survival-badges/tier-1.json'

```

- [x] Verify Tier 1 badge metadata

```
curl -L --max-redirs 4 -X GET $(engine terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_1_POOL_ID)
```

- [x] Tier 2 badge

```
engine terminus set-uri \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --pool-id $TIER_2_POOL_ID \
    --pool-uri 'https://badges.moonstream.to/cu-survival-badges/tier-2.json'

```

- [x] Verify Tier 2 badge metadata

```
curl -L --max-redirs 4 -X GET $(engine terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_2_POOL_ID)
```

- [x] Tier 3 badge

```
engine terminus set-uri \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --pool-id $TIER_3_POOL_ID \
    --pool-uri 'https://badges.moonstream.to/cu-survival-badges/tier-3.json'

```

- [x] Verify Tier 3 badge metadata

```
curl -L --max-redirs 4 -X GET $(engine terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_3_POOL_ID)
```

- [x] Launch badge

```
engine terminus set-uri \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --pool-id $LAUNCH_BADGE_POOL_ID \
    --pool-uri 'https://badges.moonstream.to/cu-launch-badge/metadata.json'

```

- [x] Verify Launch badge metadata

```
curl -L --max-redirs 4 -X GET $(engine terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $LAUNCH_BADGE_POOL_ID)
```


### Transfer pool control to Dropper contract

- [x] Tier 1 badge

```
engine terminus set-pool-controller \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $TIER_1_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Tier 2 badge

```
engine terminus set-pool-controller \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $TIER_2_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Tier 3 badge

```
engine terminus set-pool-controller \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $TIER_3_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Launch badge

```
engine terminus set-pool-controller \
    --network $BROWNIE_NETWORK \
    --address $CU_TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $LAUNCH_BADGE_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```


- [x] Verify
```

engine terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_1_POOL_ID
engine terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_2_POOL_ID
engine terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_3_POOL_ID
engine terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $LAUNCH_BADGE_POOL_ID

```

### Create claims on Dropper contract

- [x] Tier 1

```

engine dropper create-claim \
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

- [x] `export TIER_1_CLAIM_ID=$(engine dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```

engine dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_1_CLAIM_ID

```

(`21`)

- [x] Tier 2

```

engine dropper create-claim \
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

- [x] `export TIER_2_CLAIM_ID=$(engine dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```

engine dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_2_CLAIM_ID

```

(`22`)

- [x] Tier 3

```

engine dropper create-claim \
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

- [x] `export TIER_3_CLAIM_ID=$(engine dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```

engine dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_3_CLAIM_ID

```

(`23`)

- [x] Launch Badge

```

engine dropper create-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --token-type $CLAIM_TYPE \
    --token-address $CU_TERMINUS_ADDRESS \
    --token-id $LAUNCH_BADGE_POOL_ID \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] `export LAUNCH_BADGE_CLAIM_ID=$(engine dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [x] Verify

```

engine dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $LAUNCH_BADGE_CLAIM_ID

```

(`24`)


## Set signer

- [x] Get signer public key:

```
export SIGNER_ADDRESS=<redacted>
```

- [x] Tier 1

```
engine dropper set-signer-for-claim \
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
engine dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_1_CLAIM_ID
```

- [x] Tier 2

```
engine dropper set-signer-for-claim \
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
engine dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_2_CLAIM_ID
```

- [x] Tier 3

```
engine dropper set-signer-for-claim \
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
engine dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_3_CLAIM_ID
```

- [x] Launch badge

```
engine dropper set-signer-for-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --claim-id $LAUNCH_BADGE_CLAIM_ID \
    --signer-arg $SIGNER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [x] Verify:

```
engine dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $LAUNCH_BADGE_CLAIM_ID
```


## Set claim URIs

### Tier 1

- [x] Get metadata from Terminus:

```
TIER_1_URI=$(engine terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_1_POOL_ID)
```

- [x] Set claim URI

```
engine dropper set-claim-uri \
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
engine dropper claim-uri --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_1_CLAIM_ID
```

### Tier 2

- [x] Get metadata from Terminus:

```
TIER_2_URI=$(engine terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_2_POOL_ID)
```

- [x] Set claim URI

```
engine dropper set-claim-uri \
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
engine dropper claim-uri --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_2_CLAIM_ID
```

### Tier 3

- [x] Get metadata from Terminus:

```
TIER_3_URI=$(engine terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $TIER_3_POOL_ID)
```

- [x] Set claim URI

```
engine dropper set-claim-uri \
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
engine dropper claim-uri --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TIER_3_CLAIM_ID
```

### Launch Badge

- [x] Get metadata from Terminus:

```
LAUNCH_BADGE_URI=$(engine terminus uri --network $BROWNIE_NETWORK --address $CU_TERMINUS_ADDRESS --pool-id $LAUNCH_BADGE_POOL_ID)
```

- [x] Set claim URI

```
engine dropper set-claim-uri \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS \
    --claim-id $LAUNCH_BADGE_CLAIM_ID \
    --uri $LAUNCH_BADGE_URI
```

- [x] Verify

```
engine dropper claim-uri --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $LAUNCH_BADGE_CLAIM_ID
```


## Engine-db cli

### create new contract

- [ ] Verify: `engine engine-db dropper list-contracts -b $BLOCKCHAIN_NAME`

- [ ] `export DROPPER_CONTRACT_ID=<redacted>`

- [ ] `export ADMIN_TERMINUS_ADDRESS="0x062BEc5e84289Da2CD6147E0e4DA402B33B8f796"`
- [ ] `export ADMIN_POOL_ID=10`


### Create new drops

- [x]

```
export DROP_TIER_1_TITLE="Nursery Survival Tier I Badge"
export DROP_TIER_1_DESCRIPTION="Nursery Survival Tier I Badge"
export DROP_TIER_2_TITLE="Nursery Survival Tier II Badge"
export DROP_TIER_2_DESCRIPTION="Nursery Survival Tier II Badge"
export DROP_TIER_3_TITLE="Nursery Survival Tier III Badge"
export DROP_TIER_3_DESCRIPTION="Nursery Survival Tier III Badge"
export DROP_LAUNCH_TITLE="Crypto Unicorns Launch Badge"
export DROP_LAUNCH_DESCRIPTION="Crypto Unicorns Launch Badge"
```

- [x] Set block deadline: `export BLOCK_DEADLINE=1`

- [x] Tier 1
```
engine engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_TIER_1_TITLE" \
    --description "$DROP_TIER_1_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $ADMIN_TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $TIER_1_CLAIM_ID

```

- [x] Tier 2
```
engine engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_TIER_2_TITLE" \
    --description "$DROP_TIER_2_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $ADMIN_TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $TIER_2_CLAIM_ID

```

- [x] Tier 3
```
engine engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_TIER_3_TITLE" \
    --description "$DROP_TIER_3_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $ADMIN_TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $TIER_3_CLAIM_ID

```

- [x] Launch badge
```
engine engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_LAUNCH_TITLE" \
    --description "$DROP_LAUNCH_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $ADMIN_TERMINUS_ADDRESS \
    --terminus-pool-id $ADMIN_POOL_ID \
    --claim-id $LAUNCH_BADGE_CLAIM_ID

```

