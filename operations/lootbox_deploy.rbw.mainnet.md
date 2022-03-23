## Initial attempt

(Didn't succeed because of awkward `make` then `execute` workflow of `lootbox drop`.)

```
export NETWORK="polygon-main"
export TERMINUS_ADDRESS="0x99A558BDBdE247C2B2716f0D4cFb0E246DFB697D"
export SENDER_KEYFILE="<redacted>"
export CONFIRMATIONS=8
export GAS_PRICE="100 gwei"

export CONFIG_FILE=operations/rbw.lootboxes.config.json
```

```
lootbox core gogogo  --terminus-address $TERMINUS_ADDRESS --sender $SENDER_KEYFILE --network $NETWORK --gas-price "$GAS_PRICE" --confirmations $CONFIRMATIONS
```

`export LOOTBOX_ADDRESS="0x3e69Ee02C37a511eaE373b73796e4133Fa5D903D"`

```
lootbox core create-lootboxes-from-config --network $NETWORK --config-file $CONFIG_FILE --sender $SENDER_KEYFILE --address $LOOTBOX_ADDRESS --gas-price "$GAS_PRICE"
```

```
lootbox core create-lootboxes-from-config --network $NETWORK --config-file operations/interrupted.config.json --sender $SENDER_KEYFILE --address $LOOTBOX_ADDRESS --gas-price "$GAS_PRICE" --confirmations $CONFIRMATIONS
```

```
lootbox core create-lootboxes-from-config --network $NETWORK --config-file operations/interrupted2.config.json --sender $SENDER_KEYFILE --address $LOOTBOX_ADDRESS --gas-price "$GAS_PRICE" --confirmations $CONFIRMATIONS
```

```
LOOTBOX_URI=$(jq -r ".[5].tokenUri" operations/rbw.lootboxes.config.json )
echo $LOOTBOX_URI
lootbox lootbox set-lootbox-uri --network polygon-main --address $LOOTBOX_ADDRESS --sender $SENDER_KEYFILE --gas-price "$GAS_PRICE" --confirmations 2 --lootbox-id 5 --uri $LOOTBOX_URI
```

```
LOOTBOX_URI=$(jq -r ".[13].tokenUri" operations/rbw.lootboxes.config.json )
echo $LOOTBOX_URI
lootbox lootbox set-lootbox-uri --network polygon-main --address $LOOTBOX_ADDRESS --sender $SENDER_KEYFILE --gas-price "$GAS_PRICE" --confirmations 2 --lootbox-id 13 --uri $LOOTBOX_URI
```

```
lootbox drop make -i data/rbw.mainnet.csv -c data/rbw.mainnet.checkpoint.json -o data/rbw.mainnet.jobs.json
```

```
time lootbox drop execute --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.checkpoint.json \
    -i data/rbw.mainnet.jobs.json \
    -N 200
```

After adding `--errors` option to `lootbox drop execute` command:

```
time lootbox drop execute --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.checkpoint.json \
    -e data/rbw.mainnet.errors.json \
    -i data/rbw.mainnet.jobs.json \
    -N 200
```

```
lootbox lootbox set-lootbox-uri --network polygon-main --address $LOOTBOX_ADDRESS --sender $SENDER_KEYFILE --gas-price "$GAS_PRICE" --confirmations 2 --lootbox-id 0 --uri "https://s3.amazonaws.com/static.simiotics.com/terminus/deprecated.json"
```

## Reboot

```
export NETWORK="polygon-main"
export TERMINUS_ADDRESS="0x99A558BDBdE247C2B2716f0D4cFb0E246DFB697D"
export SENDER_KEYFILE="<redacted>"
export CONFIRMATIONS=8
export GAS_PRICE="100 gwei"

export CONFIG_FILE=operations/rbw.lootboxes.config.json
```

We did a bunch of withdraw ERC20 operations on Lootbox and Terminus contract.

```
lootbox core gogogo  --terminus-address $TERMINUS_ADDRESS --sender $SENDER_KEYFILE --network $NETWORK --gas-price "$GAS_PRICE" --confirmations $CONFIRMATIONS
```

`export LOOTBOX_ADDRESS="0x58E38E988ACD620b1f9de314302E897175C5161d"`

Transfer 2 WETH to lootbox

```
lootbox core create-lootboxes-from-config --network $NETWORK --config-file $CONFIG_FILE --sender $SENDER_KEYFILE --address $LOOTBOX_ADDRESS --gas-price "$GAS_PRICE" --confirmations $CONFIRMATIONS
```

```
lootbox drop make -i data/rbw.mainnet.50.csv -c data/rbw.mainnet.50.checkpoint.json -o data/rbw.mainnet.50.jobs.json
```

```
time lootbox drop execute --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.50.checkpoint.json \
    -e data/rbw.mainnet.50.errors.json \
    -i data/rbw.mainnet.50.jobs.json \
    -N 200
```

```
lootbox drop make -i data/rbw.mainnet.7500.csv -c data/rbw.mainnet.7500.checkpoint.json -o data/rbw.mainnet.7500.jobs.json
```

```
time lootbox drop execute --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.7500.checkpoint.json \
    -e data/rbw.mainnet.7500.errors.json \
    -i data/rbw.mainnet.7500.jobs.json \
    -N 200
```

```
lootbox drop make -i data/rbw.mainnet.100-250.csv -c data/rbw.mainnet.100-250.checkpoint.json -o data/rbw.mainnet.100-250.jobs.json
```

```
time lootbox drop execute --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.100-250.checkpoint.json \
    -e data/rbw.mainnet.100-250.errors.json \
    -i data/rbw.mainnet.100-250.jobs.json \
    -N 200
```

```
lootbox drop make -i data/rbw.mainnet.500-750.csv -c data/rbw.mainnet.500-750.checkpoint.json -o data/rbw.mainnet.500-750.jobs.json
```

```
time lootbox drop execute --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.500-750.checkpoint.json \
    -e data/rbw.mainnet.500-750.errors.json \
    -i data/rbw.mainnet.500-750.jobs.json \
    -N 200
```

```
lootbox drop make -i data/rbw.mainnet.1000-1500.csv -c data/rbw.mainnet.1000-1500.checkpoint.json -o data/rbw.mainnet.1000-1500.jobs.json
```

```
time lootbox drop execute --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.1000-1500.checkpoint.json \
    -e data/rbw.mainnet.1000-1500.errors.json \
    -i data/rbw.mainnet.1000-1500.jobs.json \
    -N 200
```

```
lootbox drop make -i data/rbw.mainnet.2000-2500.csv -c data/rbw.mainnet.2000-2500.checkpoint.json -o data/rbw.mainnet.2000-2500.jobs.json
```

```
time lootbox drop execute --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.2000-2500.checkpoint.json \
    -e data/rbw.mainnet.2000-2500.errors.json \
    -i data/rbw.mainnet.2000-2500.jobs.json \
    -N 200
```

```
lootbox drop make -i data/rbw.mainnet.3000-4000.csv -c data/rbw.mainnet.3000-4000.checkpoint.json -o data/rbw.mainnet.3000-4000.jobs.json
```

```
time lootbox drop execute --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.3000-4000.checkpoint.json \
    -e data/rbw.mainnet.3000-4000.errors.json \
    -i data/rbw.mainnet.3000-4000.jobs.json \
    -N 200
```

```
lootbox drop make -i data/rbw.mainnet.5000-10000.csv -c data/rbw.mainnet.5000-10000.checkpoint.json -o data/rbw.mainnet.5000-10000.jobs.json
```

```
time lootbox drop execute --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.5000-10000.checkpoint.json \
    -e data/rbw.mainnet.5000-10000.errors.json \
    -i data/rbw.mainnet.5000-10000.jobs.json \
    -N 200
```

## **GG, WP!**

## **GLHF** PART 2

### retry operations

## 100-250

Note errors file had two batches. One batch had in fact successfully been processed:
https://polygonscan.com/tx/0x13d3c3cb990c18d89dfad80ca8a8320805f7aed95a48b2481269f9baa1b947bd

Modified errors file to only contain failed batch.

- [x] Done

```
lootbox drop retry --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.100-250.checkpoint.json \
    -e data/rbw.mainnet.100-250.errors.json \
    -i data/rbw.mainnet.100-250.jobs.json \
    -N 200
```

## 500-750

Note: The following transactions were incorrectly marked as errors before:
- https://polygonscan.com/tx/0x85b0cedc62e8887ac8f87ee1d3f39b771b2e3fe1f4cd8cbb7cb7235b67dbaa25
- https://polygonscan.com/tx/0x9d72343e6411f8b20f910940573cfe1519ea098835597e0f3f2f11344f5db6a6

Removed those arguments from the errors array.

- [x] Done

```
lootbox drop retry --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.500-750.checkpoint.json \
    -e data/rbw.mainnet.500-750.errors.json \
    -i data/rbw.mainnet.500-750.jobs.json \
    -N 200
```

Transactions:
- https://polygonscan.com/tx/0x4411a763acd24fd57300aef0a942d689a575c25aec3b9d01f4404f60c255ddbb
- https://polygonscan.com/tx/0xa14e755032568afac6cd711f9c09311b586c9abfb44a786572f7fe6a24c2fec3
- https://polygonscan.com/tx/0xffc0f2cf099e7826c64ac9a97aa3c2d47a9eb0dca582d83fd4caea83c3d94d9b

## 1000-1500

No work necessary. Errors were incorrectly marked.

Successful transaction: https://polygonscan.com/tx/0x5bd0a5febc8a3d574b17ecf9c5574ad8561422c2966b87f71db1d79f384a524e

- [x] Done

```
drop retry --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.1000-1500.checkpoint.json \
    -e data/rbw.mainnet.1000-1500.errors.json \
    -i data/rbw.mainnet.1000-1500.jobs.json \
    -N 200
```

## 2000-2500
- [x] Done

```
lootbox drop retry --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.2000-2500.checkpoint.json \
    -e data/rbw.mainnet.2000-2500.errors.json \
    -i data/rbw.mainnet.2000-2500.jobs.json \
    -N 200
```

## 5000-10000
- [x] Done

```
lootbox drop retry --network $NETWORK \
    --address $LOOTBOX_ADDRESS \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
    --confirmations 2 \
    -c data/rbw.mainnet.5000-10000.checkpoint.json \
    -e data/rbw.mainnet.5000-10000.errors.json \
    -i data/rbw.mainnet.5000-10000.jobs.json \
    -N 200
```

Transactions:
- https://polygonscan.com/tx/0xf16500682652f9758958ec3c75c188f02431cf1c4966bba5674d9effa470c798
