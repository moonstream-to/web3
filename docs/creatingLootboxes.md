```
lootbox lootbox create-lootbox --network polygon-test --address $LOOTBOX_ADDRESS --gas-price "100 gwei" --items  ./lootboxItems.json --sender .secrets/dev.json
```

Get count:
```
lootbox lootbox total-lootbox-count --address $LOOTBOX_ADDRESS  --network polygon-test 
```

`ID=previous command result - 1`

Get lootboxItem:
```
lootbox lootbox get-lootbox-item-by-index --lootbox-id $ID --item-index 0  --address $LOOTBOX_ADDRESS  --network polygon-test 
```

```
lootbox lootbox set-lootbox-uri --uri https://arweave.net/6xTnkIR5C9ARys_tWWC5SSJSQsSmBBsAfAEQVa2B6no  --network polygon-test --sender .secrets/dev.json --password y --address $LOOTBOX_ADDRESS --lootbox-id $ID --gas-price "100 gwei" 
```