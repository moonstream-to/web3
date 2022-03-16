
## Showing the lootboxes on frontend:
After user connects wallet:
1. Get the total number of the lootboxes: `totalLootboxCount()`
2. Iterate on `lootboxIds` from `0 -> lootboxesCount`, 
    1. To get user's lootbox balance: `getLootboxBalance(lootboxId, userAddress)`
    2. To get lootbox uri: `getLootboxURI(lootboxId)`

# **Note**:
**Load the data in asynchronous way.**

```javascript
function loadLootboxBalances(userAddress) {
    let totalLootboxCount = await lootboxContract.totalLootboxCount();
    for (let i = 0; i < totalLootboxCount; ++i) {
        lootboxContract.getLootboxBalance(i, userAddress).call().then((balance)=>{
            //change state here
        })
    }
}
```

## To open lootbox:
1. `openLootbox(lootboxId, count)`, count is number of lootboxes for `lootboxId` type user wants to open 

