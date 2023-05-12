# waggle

`waggle` is a command-line tool which allows Moonstream users to:

1. Certify drop claims for Dropper v0.2.0
2. Manage signing accounts
3. Send drop claims to the Moonstream Engine API

### Installation

```
go install github.com/bugout-dev/engine/waggle
```

### Usage

```
waggle -h
```

#### Manage accounts

You can import a signing account from an external wallet using its private key:

```
waggle accounts import -k <path at which to save keystore file>
```

This command will prompt you for the private key.

#### Sign Dropper claims

You can sign a single claim using:

```bash
waggle sign dropper single -k <path to signing account keystore file> \
    --chain-id <chain id for blockchain to which Dropper is deployed - 137 for Polygon> \
    --dropper <address of Dropper on that chain> \
    --amount <amount of tokens to distribute in claim> \
    --block-deadline <claim will expire after this block number> \
    --claimant <address of claimant> \
    --drop-id <drop id that claim refers to> \
    --request-id <a request id for this claim - should be unique over all claims on this drop>
```

For example, this is how I would create a claim for the dead address on Mumbai testnet:

```bash
waggle sign dropper single -k signer.json \
    --chain-id 80001 \
    --dropper 0x4ec36E288E1b5d6914851a141cb041152Cf95328 \
    --amount 3000000000000000000 \
    --block-deadline 40000000 \
    --claimant 0x000000000000000000000000000000000000dEaD \
    -drop-id 2 \
    --request-id 279927661987246322371885526670387588087
```

You can also sign claims in batches using `waggle sign dropper batch`.

The easiest way to do this is to start with a JSON file containing a batch of
claims (`batch.json` below):

```json
[
  {
    "dropId": "2",
    "requestID": "5",
    "claimant": "0x000000000000000000000000000000000000dEaD",
    "blockDeadline": "40000000",
    "amount": "3000000000000000000"
  },
  {
    "dropId": "2",
    "requestID": "6",
    "claimant": "0x000000000000000000000000000000000000dEaD",
    "blockDeadline": "40000000",
    "amount": "3000000000000000000"
  },
  {
    "dropId": "2",
    "requestID": "7",
    "claimant": "0x000000000000000000000000000000000000dEaD",
    "blockDeadline": "40000000",
    "amount": "3000000000000000000"
  },
  {
    "dropId": "2",
    "requestID": "8",
    "claimant": "0x000000000000000000000000000000000000dEaD",
    "blockDeadline": "40000000",
    "amount": "3000000000000000000"
  }
]
```

To sign this batch of claims:

```bash
waggle sign dropper batch -k signer.json \
    --chain-id 80001 \
    --dropper 0x4ec36E288E1b5d6914851a141cb041152Cf95328 \
    --infile batch.json \
    --outfile signed_batch.json
```

This results in a file that looks like this:

```json
[
  {
    "dropId": "2",
    "requestID": "5",
    "claimant": "0x000000000000000000000000000000000000dEaD",
    "blockDeadline": "40000000",
    "amount": "3000000000000000000",
    "signature": "408...",
    "signer": "<redacted Ethereum address>"
  },
  {
    "dropId": "2",
    "requestID": "6",
    "claimant": "0x000000000000000000000000000000000000dEaD",
    "blockDeadline": "40000000",
    "amount": "3000000000000000000",
    "signature": "667...",
    "signer": "<redacted Ethereum address>"
  },
  {
    "dropId": "2",
    "requestID": "7",
    "claimant": "0x000000000000000000000000000000000000dEaD",
    "blockDeadline": "40000000",
    "amount": "3000000000000000000",
    "signature": "5c6...",
    "signer": "<redacted Ethereum address>"
  },
  {
    "dropId": "2",
    "requestID": "8",
    "claimant": "0x000000000000000000000000000000000000dEaD",
    "blockDeadline": "40000000",
    "amount": "3000000000000000000",
    "signature": "85f...",
    "signer": "<redacted Ethereum address>"
  }
]
```

#### Send signed claims to Moonstream API

You do this using the `waggle moonstream drop` command. You should first store your Moonstream API access
token under the `MOONSTREAM_ENGINE_ACCESS_TOKEN` environment variable:

```
export MOONSTREAM_ENGINE_ACCESS_TOKEN=<token>
```

You can generate an access token at https://moonstream.to/app

Then:

```
waggle moonstream drop \
    --contract-id a035f3f8-7301-45b7-940a-109585419774 \
    --infile signed_batch.json
    --ttl-days 30
```

This requires that you have already told Moonstream about the Dropper contract in question as a
contract you want your users to be able to claim against. To get the `--contract-id`, you can use
the `waggle moonstream contracts` command.

The above `waggle moonstream drop` command submits the signed claims and tells the API that it would be
okay to delete them after 30 days.

Your users can view all open claims that they can execute by hitting the following URL:

```
https://engineapi.moonstream.to/contracts/requests?contract_id=$CONTRACT_ID&caller=$USER_ADDRESS
```

Here, `$CONTRACT_ID` should be the same contract ID you used in `waggle moonstream drop`. `$USER_ADDRESS`
is the user's Ethereum account address.


#### Get claim requests from Bugout journal

```
waggle sign dropper pull \
  --cursor <cursor name> \
  -j <Bugout Journal ID> \
  >unsigned.csv
```

This expects a `BUGOUT_ACCESS_TOKEN` environment variable to be set. You can generate an access token
at https://bugout.dev/account/tokens. Once you have generated a token, set it in your shell session using:

```
export BUGOUT_ACCESS_TOKEN=<token>
```

(For example: `export BUGOUT_ACCESS_TOKEN=61884ddf-46aa-434f-b489-53819cfa2307`)

This will only pull messages that were sent to the Bugout journal since the last time you queried it with
the same cursor.

The data comes down as a CSV file that looks like this:

```
dropId,requestID,claimant,blockDeadline,amount,signer,signature
1,115720181650977233700713231242528612405061886387364945891853856642923,0x0DEFbcF39bC9035262e3E5C1c72a82299B542bAF,95351184,500000000000000000000,,
```

You can sign this using the `waggle sign dropper batch command` by passing the CSV file as the `--infile`
argument and setting the `--csv` flag:

```
waggle sign dropper batch -k signer.json \
    --chain-id 80001 \
    --dropper 0x4ec36E288E1b5d6914851a141cb041152Cf95328 \
    --infile unsigned.csv \
    --csv \
    --outfile signed_batch.json

```

### Build

```
go build ./...
./waggle -h
```

### Test

```
go test ./... -v
```
