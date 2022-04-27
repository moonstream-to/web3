# enviroment variables

```
- [x] MOONSTREAM_CORS_ALLOWED_ORIGINS
- [x] AWS_DEFAULT_REGION
- [x] MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID
- [x] MOONSTREAM_AWS_SIGNER_IMAGE_ID
- [x] `export ENGINE_DB_URI=""`
- [ ] `export BROWNIE_NETWORK=polygon-main`
- [ ] `export TERMINUS_ADDRESS=""`
- [x] `export SENDER=<keystore path>`
- [x] `export SENDER_ADDRESS=$(jq -r .address $SENDER)`
- [ ] `export SENDER_KEYFILE=""`
- [ ] `export CONFIRMATIONS=5`
- [ ] `export GAS_PRICE="100 gwei"`
- [ ] `export CLAIM_TYPE=1`
```

# Deploy Dropper contract on mainnet

```
lootbox dropper deploy --network $BROWNIE_NETWORK --sender $SENDER_KEYFILE  --gas-price $GAS_PRICE --confirmations $CONFIRMATIONS
```

- [ ] `export DROPPER_ADDRESS=""`

# Get pool ids of lootyboxes

4, 5, 6

Check pool uri

## Common

```
curl -L --max-redirs 4 -X GET $(terminus uri --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id 4)
```

## Rare

```
curl -L --max-redirs 4 -X GET $(terminus uri --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id 5)
```

## Mythical

```

curl -L --max-redirs 4 -X GET $(terminus uri --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id 6)

```

- [ ] `export TERMINUS_COMMON_LOOTBOX_POOL_ID=""`
- [ ] `export TERMINUS_RARE_LOOTBOX_POOL_ID=""`
- [ ] `export TERMINUS_MYTH_LOOTBOX_POOL_ID=""`

Return pool control to owner of DarkForest contract lootboxes and eggs in one moment

```

dark-forest surrender-terminus-pools --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --sender $SENDER_KEYFILE --gas-price $GAS_PRICE --confirmations $CONFIRMATIONS

```

## Check pool controller

```

[$(terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id 1) == $SENDER_ADDRESS] && echo "OK"

```

```

terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id 2

```

```

terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id 3

```

```

terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id 4

```

```

terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id 5

```

```

terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id 6

```

### Transfer pool control to dropper contract

## move control of pool to dropper contract

- [ ] Transfer control of pool 4 to dropper contract

```

lootbox terminus set-pool-controller \
 --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $TERMINUS_COMMON_LOOTBOX_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

- [ ] Transfer control of pool 5 to dropper contract

```

lootbox terminus set-pool-controller \
 --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $TERMINUS_RARE_LOOTBOX_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

- [ ] Transfer control of pool 6 to dropper contract

```

lootbox terminus set-pool-controller \
 --network $BROWNIE_NETWORK \
    --address $TERMINUS_ADDRESS \
    --sender $SENDER \
    --pool-id $TERMINUS_MYTH_LOOTBOX_POOL_ID \
    --new-controller $DROPPER_ADDRESS \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

- [ ] Verify

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id $TERMINUS_COMMON_LOOTBOX_POOL_ID

```

- [ ] Verify

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id $TERMINUS_RARE_LOOTBOX_POOL_ID

```

- [ ] Verify

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id $TERMINUS_MYTH_LOOTBOX_POOL_ID

```

## Create Drop on contract common lootbox

- [ ] Create claim common lootbox

```

lootbox dropper create-claim \
 --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --token-type $CLAIM_TYPE \
    --token-address $TERMINUS_ADDRESS \
    --token-id $TERMINUS_COMMON_LOOTBOX_POOL_ID \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

- [ ] `export COMMON_LOOTBOX_CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [ ] Verify

```

lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $COMMON_LOOTBOX_CLAIM_ID

```

# Create Drop on contract rare lootbox

- [ ] Create claim rare lootbox

```

lootbox dropper create-claim \
 --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --token-type $CLAIM_TYPE \
    --token-address $TERMINUS_ADDRESS \
    --token-id $TERMINUS_RARE_LOOTBOX_POOL_ID \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

- [ ] `export RARE_LOOTBOX_CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [ ] Verify

```

lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $RARE_LOOTBOX_CLAIM_ID

```

# Create Drop on contract myth lootbox

- [ ] Create claim myth lootbox

```

lootbox dropper create-claim \
 --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --token-type $CLAIM_TYPE \
    --token-address $TERMINUS_ADDRESS \
    --token-id $TERMINUS_MYTH_LOOTBOX_POOL_ID \
    --amount 1 \
    --gas-price "$GAS_PRICE" \
 --confirmations $CONFIRMATIONS

```

- [ ] `export MYTH_LOOTBOX_CLAIM_ID=$(lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS)`

- [ ] Verify

```

lootbox dropper get-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $MYTH_LOOTBOX_CLAIM_ID

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
    --claim-id $COMMON_LOOTBOX_CLAIM_ID \
    --signer-arg $SIGNER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [ ] Verify:

```
lootbox dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $COMMON_LOOTBOX_CLAIM_ID
```

### Set signer on pool common lootbox

- [ ] Set signer for claim:

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

- [ ] Verify:

```
lootbox dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $RARE_LOOTBOX_CLAIM_ID
```

### Set signer on pool common lootbox

- [ ] Set signer for claim:

```
lootbox dropper set-signer-for-claim \
    --network $BROWNIE_NETWORK \
    --address $DROPPER_ADDRESS \
    --sender $SENDER \
    --claim-id $MYTH_LOOTBOX_CLAIM_ID \
    --signer-arg $SIGNER_ADDRESS \
    --gas-price "$GAS_PRICE" \
    --confirmations $CONFIRMATIONS

```

- [ ] Verify:

```
lootbox dropper get-signer-for-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --claim-id $TERMINUS_MYTH_LOOTBOX_POOL_ID
```

# Engine-db cli

## create new contract

- [ ] Create row:

```
lootbox engine-db dropper create-contract -b polygon \
                                          -a $DROPPER_ADDRESS \
                                          -t "Our NEW Dropper contract" \
                                          -d "This is a dropper contract(capitan)" \
                                          -i "image-uri"
```

- [ ] Verify: `lootbox engine-db dropper list-contracts -b $BLOCKCHAIN_NAME`

- [ ] `export DROPPER_CONTRACT_ID=<primary key id for contract>`

## Create new drops

- [ ] Create title COMMON_LOOTBOX for drop: `export DROP_COMMON_LOOTBOX_TITLE="Any title"`

- [ ] Create description COMMON_LOOTBOX for drop: `export DROP_COMMON_LOOTBOX_DESCRIPTION="Any description"`

- [ ] Create title RARE_LOOTBOX for drop: `export DROP_RARE_LOOTBOX_TITLE="Any title"`

- [ ] Create description RARE_LOOTBOX for drop: `export DROP_RARE_LOOTBOX_DESCRIPTION="Any description"`

- [ ] Create title MYTH_LOOTBOX for drop: `export DROP_MYTH_LOOTBOX_TITLE="Any title"`

- [ ] Create description MYTH_LOOTBOX for drop: `export DROP_MYTH_LOOTBOX_DESCRIPTION="Any description"`

- [ ] Set block deadline: `export BLOCK_DEADLINE=<whatever>`

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_COMMON_LOOTBOX_TITLE" \
    --description "$DROP_COMMON_LOOTBOX_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $TERMINUS_ADDRESS \
    --terminus-pool-id $TERMINUS_COMMON_LOOTBOX_POOL_ID \
    --claim-id $COMMON_LOOTBOX_CLAIM_ID

```

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_TITLE" \
    --description "$DROP_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $TERMINUS_ADDRESS \
    --terminus-pool-id $TERMINUS_RARE_LOOTBOX_POOL_ID \
    --claim-id $RARE_LOOTBOX_CLAIM_ID

```

```
lootbox engine-db dropper create-drop --dropper-contract-id $DROPPER_CONTRACT_ID \
    --title "$DROP_TITLE" \
    --description "$DROP_DESCRIPTION" \
    --block-deadline $BLOCK_DEADLINE \
    --terminus-address $TERMINUS_ADDRESS \
    --terminus-pool-id $TERMINUS_MYTH_LOOTBOX_POOL_ID \
    --claim-id $MYTH_LOOTBOX_CLAIM_ID

```

- [ ] List drops:

```
lootbox engine-db dropper list-drops \
    --dropper-contract-id $DROPPER_CONTRACT_ID \
    -a false
```

- [ ] `export DB_COMMON_LOOTBOX_CLAIM_ID=<id of claim you just created>`
- [ ] `export DB_RARE_LOOTBOX_CLAIM_ID=<id of claim you just created>`
- [ ] `export DB_MYTH_LOOTBOX_CLAIM_ID=<id of claim you just created>`

## Set claims to active

- [x] Set claim as active (in `psql`):

```bash
psql $ENGINE_DB_URI -c "UPDATE dropper_claims SET active = true WHERE id in ('$DB_COMMON_LOOTBOX_CLAIM_ID','$DB_RARE_LOOTBOX_CLAIM_ID','$DB_MYTH_LOOTBOX_CLAIM_ID');"
```
