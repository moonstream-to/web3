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


- [x] Verify

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id $TERMINUS_COMMON_LOOTBOX_POOL_ID

```

- [x] Verify

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id $TERMINUS_RARE_LOOTBOX_POOL_ID

```

- [x] Verify

```

lootbox terminus terminus-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --pool-id $TERMINUS_MYTH_LOOTBOX_POOL_ID

```




# Create Drop on contract

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


# Create Drop on contract

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


# Create Drop on contract

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


```
