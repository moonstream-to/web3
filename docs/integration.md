# Lootbox doc

## **Lootbox Item**
Lootboxes are consist of `lootbox items`. Lootbox item has following properties:
- `uint256 rewardType`: Reward type of lootbox Item
- `address tokenAddress`: Address of the lootbox reward token
- `uint256 tokenId`: Token Id of the reward token. *(Only for ERC1155. For ERC20 put `0`)*
- `uint256 amount`: Amount of the token reward *(For ERC20 amount should be in decimal form)*
- `uint256 weight`: Weight of the lootbox item for lootbox with **random** type. *(Put 0 for **ordinary** lootbox types)*

### Reward Types:
- ERC20: `0`
- ERC1155: `1155`


## **Lootbox Types**
- **Ordinary lootbox** - When user opens this type of lootbox, he will get all lootbox items inside that lootbox
- **Random lootbox Type1** - When user opens this type of lootbox, he will get only 1 random item with the given item weights

### constants for lootbox types:
- **Ordinary lootbox**: `0`
- **Random lootbox Type1**: `1`

## Lootboxes structure:
Lootboxes are consist of following params:
- `uint256 lootboxType`: type of the lootbox
- `LootboxItem[] lootboxItems`: array of lootbox items


# Lootbox user experience:
## Initialzie lootbox contract:
```javaScript
let web3 = new Web3(window.ethereum)
let lootboxContract = new web3.eth.Contract(lootboxAbi, lootboxContractAddress)
```
## Showing all lootboxes:
```javaScript
async function loadLooboxes(){
    let lootboxesCount = await lootboxContract.methods.totalLootboxCount().call();
    for (let i = 1; i <lootboxesCount; i++) {
        let lootboxUri = lootboxContract.methods.getLootboxURI.call().then(async (uri) => {
            let metadata = await fetch(uri);
            render(metadata);
        })
    }
}
```
**Important**: make the loading asynchronously, so user doesn't need to wait for all lootboxes. There could be lots of lootboxes, and if lootboxes that are not fetched will be blocking render of already fetched, user might think that the website is frozen/not working. 

### lootbox metadata example:
```json
{
    "name": "500 Rainbow Token Pack",
    "description": "A big fistful of RBW tokens!\nTrade it on OpenSea or redeem at www.cryptounicorns.fun later this year!",
    "image": "https://arweave.net/oFPXxggajt5cOm7zaPckmdXoQeKxhoFUItuxNoJ1Dck",
    "external_url": "https://www.cryptounicorns.fun",
    "metadata_version": 1,
    "attributes": [
        {
            "trait_type": "RBW Amount",
            "value": "500"
        },
        {
            "trait_type": "Game",
            "value": "Crypto Unicorns"
        }
    ]
}
```


## Getting balance of user for `lootboxId`:
```javaScript
async function getLootboxBalance(lootboxId, userAddress) {
    return lootboxContract.methods.getLootboxBalance(lootboxId, userAddress).call()
}
```

## Opening lootbox:
### Get Lootbox type:
```javascript
let lootboxType = lootboxConract.methods.lootboxTypebyLootboxId(lootboxId).call()
```
## TODO: make promise, resolve
### Opening ordinary lootbox:
```javaScript

async function sendTransaction(tx) {
    tx.send({from: window.ethereum.selectedAddress})
    .on('transactionHash', function (hash) {
            console.log("Transaction hash: " + hash)
        })
    .on('receipt', function (receipt) {
            console.log("Transaction receipt: " + receipt)
            setBalance()
        })
    .on('error', function (error) {
            console.log("Transaction error: " + error)
        }
        )
}

async function openOrdinaryLootbox(lootboxId, count) {
    let tx = await lootboxContract.methods.openLootbox(lootboxId, count)
    await sendTransaction(tx)
}
```

### Opening random lootbox:
In order to open random lootbox:
- start opening the lootbox
- check if lootboxOpening is ready (random number is determined)
- complete opening
```javaScript

async function checkUsersActiveLootboxOpeningStatus(userAddress) {
    let currentOpeningforUser = lootboxContract.methods.CurrentLootboxOpeningForUser(userAddress).call()
    if (currentOpeningforUser == 0) {
        return null // no active opening
    }
    let lootboxOpening = lootboxContract.methods.ActiveLootboxOpenings(currentOpeningforUser).call()

    return {status: lootboxOpening.status, lootboxId: lootboxOpening.lootboxId}
}

async function startRandomLootboxOpening(lootboxId) {
    let userAddress = window.ethereum.selectedAddress;
    let activeOpening = await checkUsersActiveLootboxOpeningStatus(userAddress)
    if (activeOpening != null) {
        console.log("User already has active opening")
        return
    }

    const count = 1; // you can open only 1 random lootbox at a time
    await openOrdinaryLootbox(lootboxId, count)

}

async function completeRandomLootboxOpening() {
    let activeOpening = await checkUsersActiveLootboxOpeningStatus(window.ethereum.selectedAddress)

    if (activeOpening == null) {
        console.log("User has no active opening")
        return
    }

    await sendTransaction(lootboxContract.methods.completeRandomLootboxOpening(activeOpening.lootboxId))

}


```

