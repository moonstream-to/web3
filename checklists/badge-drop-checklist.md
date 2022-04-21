# Checklist Founders Badge List 4.18

# set enviroment variable

- [ ] MOONSTREAM_CORS_ALLOWED_ORIGINS
- [ ] AWS_DEFAULT_REGION
- [ ] MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID
- [ ] MOONSTREAM_AWS_SIGNER_IMAGE_ID
- [ ] BROWNIE_NETWORK
- [ ] ENGINE_DB_URI
- [ ] TERMINUS_MINTABLE_TYPE

# Deploy Dropper contract

```
lootbox dropper deploy --network $BROWNIE_NETWORK --sender .secrets/<owner-key-store> ----confirmations 5
```

# set enviroment variable

[ ] - DROPPER_CONTRACT

# Create terminus batch pool if not created yeat

```
dao terminus create-pool-v1 --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --sender .secrets/<owner-key-store> --transferable-arg <badges-capacity> --transferable-arg False --burnable-arg False

```

```
dao terminus total-pools --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS

```

## move contractroll of pool to dropper contract

```
dao terminus set-pool-controller --network $BROWNIE_NETWORK --address $TERMINUS_ADDRESS --sender .secrets/<owner-key-store> --pool-id $TERMINUS_POOL_ID --controller-address $DROPPER_CONTRACT

```

# set enviroment variable

[ ] - $BADGE_POOL_ID

# Create Drop on contract

```
lootbox dropper create-claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --sender .secrets/<owner-key-store> --token-type $TERMINUS_MINTABLE_TYPE --token-address $TERMINUS_ADDRESS --token-id $BADGE_POOL_ID --amount 1

```

```
lootbox dropper num-claims --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS
```

# set enviroment variable

[ ] - $CLAIM_ID

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

[ ] - $DROPPER_CONTRACT_ID

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

[ ] - $DROPPER_CLAIM_ID

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
lootbox dropper claim --network $BROWNIE_NETWORK --address $DROPPER_ADDRESS --sender .secrets/<owner-key-store> --claim-id $CLAIM_ID --signature $signature --block-deadline $block_deadline --amount $amount
```
