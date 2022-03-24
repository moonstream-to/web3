```
export NETWORK="polygon-main"
export TERMINUS_ADDRESS="0x99A558BDBdE247C2B2716f0D4cFb0E246DFB697D"
export SENDER_KEYFILE="<redacted>"
export CONFIRMATIONS=8
export GAS_PRICE="100 gwei"

export CONFIG_FILE=operations/rbw.lootboxes.config.json
export LOOTBOX_ADDRESS="0x58E38E988ACD620b1f9de314302E897175C5161d"
```

# Create jobs file from matrices

```
lootbox drop make --network $NETWORK \
 --sender $SENDER_KEYFILE \
 -i 'data/Updated CopLnch List - RBW Matrix for moonstream drop.csv' \
 -c data/rbw.032422.checkpoint.json \
 -o data/rbw.032422.jobs.json

```

# Execute drops

```

lootbox drop make --network $NETWORK \
    --sender $SENDER_KEYFILE \
    --gas-price "$GAS_PRICE" \
 --confirmations 2 \
 -e data/rbw.032422.errors.json \
 -c data/rbw.032422.checkpoint.json \
 -i data/rbw.032422.jobs.json \
 -N 200

```
