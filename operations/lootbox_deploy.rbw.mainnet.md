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
