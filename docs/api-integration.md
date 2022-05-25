# Integrating with the Moonstream Engine API

## API URLs

Moonstream Engine API URL: https://engineapi.moonstream.to

Test the connection: https://engineapi.moonstream.to/ping

## Players vs. administrators

The Moonstream Engine API distinguishes between player-facing and administrator-facing functionality.

All player-facing functionality is exposed to the public via `GET` endpoints that do not require any
authentication.

All administrator-facing functionality requires the requester to pass a valid `Authorization` header
to the API in the form:

```
Authorization: moonstream <token>
```

**You DO NOT need to worry about authentication if** you are integrating with the Moonstream Engine API to allow your players to:
1. Claim tokens as part of drops
2. Open lootboxes
3. Craft items
4. Play Moonstream minigames

**You DO need to worry about authentication if** you are integrating with the Moonstream Engine API to allow your teammates to:
1. Manage drops and drop whitelists
2. Check the status of an ongoing drop
3. Create new lootboxes
4. Create new crafting recipes
5. Modify existing crafting recipes
6. Deploy Moonstream minigames for your players

## How to

### Get the first 10 drops that a user can claim on a given blockchain

You can get all the drops that a user is eligible to claim using the `/drops/batch` endpoint on the Moonstream Engine API.

To call this endpoint:

<details>
<summary><b>curl</b></summary>

```
curl "https://engineapi.moonstream.to/drops/batch?blockchain=$BLOCKCHAIN&address=$PLAYER_ADDRESS&limit=$PAGE_SIZE&offset=$PAGE_NUMBER"
```

For example, to retrieve the first 10 drops for the address `0x1010000000000000000000000000000000000000` on the `polygon`
blockchain:

```
BLOCKCHAIN=polygon PLAYER_ADDRESS=0x1010000000000000000000000000000000000000 PAGE_SIZE=10 PAGE_NUMBER=0
curl "https://engineapi.moonstream.to/drops/batch?blockchain=$BLOCKCHAIN&address=$PLAYER_ADDRESS&limit=$PAGE_SIZE&offset=$PAGE_NUMBER"
```

The response would look like this:

```
[
  {
    "claimant": "0x1010000000000000000000000000000000000000",
    "claim_id": 2,
    "amount": 100,
    "amount_string": "100",
    "block_deadline": 29029492,
    "signature": "502ca83bc80827.....c1b",
    "dropper_claim_id": "42424242-4242-4242-4242-424242424242",
    "dropper_contract_address": "0x6bc613A25aFe159b70610b64783cA51C9258b92e",
    "blockchain": "polygon"
  },
]
```
</details>

<details>
<summary><b>fetch</b></summary>

```
fetch(`https://engineapi.moonstream.to/drops/batch?blockchain=${blockchain}&address=${playerAddress}&limit=${pageSize}&offset=${pageNumber}`)
```

For example, to retrieve the first 10 drops for the address `0x1010000000000000000000000000000000000000` on the `polygon`
blockchain:

```
let blockchain = "polygon";
let playerAddress = "0x1010000000000000000000000000000000000000";
let pageSize = 10;
let pageNumber = 0;
fetch(`https://engineapi.moonstream.to/drops/batch?blockchain=${blockchain}&address=${playerAddress}&limit=${pageSize}&offset=${pageNumber}`)
```

The response would look like this (assuming the player had only one drop eligible for claim):

```
[
  {
    "claimant": "0x1010000000000000000000000000000000000000",
    "claim_id": 2,
    "amount": 100,
    "amount_string": "100",
    "block_deadline": 29029492,
    "signature": "502ca83bc80827.....c1b",
    "dropper_claim_id": "42424242-4242-4242-4242-424242424242",
    "dropper_contract_address": "0x6bc613A25aFe159b70610b64783cA51C9258b92e",
    "blockchain": "polygon"
  },
]
```
</details>

You can use the `limit` and `offset` query parameters to page over all the claims that a user is eligible to receive.
