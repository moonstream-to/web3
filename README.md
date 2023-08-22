# moonstream-to/web3

This repository is home to [Moonstream](https://moonstream.to)'s smart contracts. It also contains
a command-line interfaces to those smart contracts.

## Structure

### Smart contracts

All smart contracts can be found in the [`contracts/`](./contracts/) directory.

Currently, we use [`brownie`](https://github.com/eth-brownie/brownie) to compile and interact with our
smart contracts.

All external dependencies are registered in [`brownie-config.yaml`](./brownie-config.yaml). To learn more
about how to use `brownie`, read the [`brownie` documentation](https://eth-brownie.readthedocs.io/en/latest/).

If you want to help us add [`hardhat`](https://hardhat.org/) or [`foundry`](https://github.com/foundry-rs/foundry)
support, your contributions will be very welcome.


### Command-line interface: `web3cli`

This repository also defines a command-line interface, `web3cli`, to Moonstream smart contracts. `web3cli`
is set up to use the `brownie` build artifacts produced by `brownie compile`. It is intended to be used
*from this repository*.

To install `web3cli`, you will need to set up a Python environment.

To do this, first [install Python 3](https://www.python.org/) (if you don't already have it installed),
and create a virtual environment:

```bash
python3 -m venv .web3
```

Then, install `web3cli` by running the following command from the root of this repository:

```bash
export BROWNIE_LIB
pip install -e cli/
```

Once this is finished:

```
$ web3cli --help
usage: web3cli [-h] {core,flows,dropper-v1,dropper,lootbox,erc20,erc721,drop,terminus,crafting,gofp,setup-drop,predicates,inventory,statblock} ...

dao: The command line interface to Moonstream DAO

positional arguments:
  {core,flows,dropper-v1,dropper,lootbox,erc20,erc721,drop,terminus,crafting,gofp,setup-drop,predicates,inventory,statblock}
    predicates          Predicates for use with Moonstream game mechanics

options:
  -h, --help            show this help message and exit
```

### ABIs

The [`abi/`](./abi/) directory contains current ABIs for all the smart contracts in this repository. You
can use these ABIs to generate interfaces to any deployed Moonstream contract.


### Tests

All tests are currently in the [`cli/web3cli/`](./cli/web3cli/) directory. Just look for files matching
`test_*.py`.

You can run tests using [`cli/test.sh`](./cli/test.sh). For example, to run Dropper tests, you would invoke
the following command (from the root of this repo):

```bash
cli/test.sh web3cli.test_dropper
```

Tests are executed against a [local Ganache network](https://github.com/trufflesuite/ganache). You will need
to use [Node JS](https://nodejs.org/en) to install Ganache:

```bash
npm install --global ganache-cli
```

## Contracts

This repository contains many contracts. Some are immutable and others are implemented using the
[EIP-2535 Diamond, Multi-Facet Proxy standard](https://eips.ethereum.org/EIPS/eip-2535).

Implementation contracts programmed under the EIP-2535 scheme are suffixed with the word `Facet`. These implementation
contracts can be used as part of any `DELEGATECALL` proxy setup.

Wherever possible, we aim to provide immutable, non-proxy implementations of our contracts. If this repository
doesn't contain an immutable implementation of the contract you are interested in, please either [create an
issue](https://github.com/moonstream-to/web3/issues/new) for it or add a comment or reaction to an issue that already exists.
This will help us prioritize the immutable implementations.

We start with proxy implementations as this helps us develop our contracts in an iterative manner using
user feedback. If you have feedback for us, [we are listening](https://discord.gg/K56VNUQGvA)!

### Terminus

Terminus is an access control protocol based on the [ERC-1155 Multi Token standard](https://eips.ethereum.org/EIPS/eip-1155).

<table>
  <tr>
    <th>Contract name</th>
    <th>Immutable or Upgradable</th>
    <th>Deployment</th>
    <th>CLI</th>
    <th>Solidity interface</th>
    <th>ABI</th>
  </tr>
  <tr>
    <td><a href="./contracts/terminus/TerminusFacet.sol"><pre>TerminusFacet</pre></a></td>
    <td>Upgradable</td>
    <td><pre>web3cli core terminus-gogogo</pre></td>
    <td><pre>web3cli terminus</pre></td>
    <td><a href="./contracts/interfaces/ITerminus.sol"><pre>ITerminus</pre></a></td>
    <td><a href="./abi/TerminusFacet.json"><pre>abi/TerminusFacet.json</pre></a></td>
  </tr>
</table>

### Dropper

Dropper is a contract that allows you to distribute tokens to your users, with *them* submitting the
transactions to claim those tokens.

It can distribute ERC20 tokens, ERC721 tokens, and ERC1155 tokens. It can also be used to mint Terminus
tokens using an authorized claim workflow.

<table>
  <tr>
    <th>Contract name</th>
    <th>Immutable or Upgradable</th>
    <th>Deployment</th>
    <th>CLI</th>
    <th>Solidity interface</th>
    <th>ABI</th>
  </tr>
  <tr>
    <td><a href="./contracts/Dropper/DropperFacet.sol"><pre>DropperFacet</pre></a></td>
    <td>Upgradable</td>
    <td><pre>web3cli core dropper-gogogo</pre></td>
    <td><pre>web3cli dropper</pre></td>
    <td><a href="./contracts/interfaces/IDropper.sol"><pre>IDropper</pre></a></td>
    <td><a href="./abi/DropperFacet.json"><pre>abi/DropperFacet.json</pre></a></td>
  </tr>
  <tr>
    <td><a href="./contracts/Dropper.sol"><pre>Dropper (legacy version)</pre></a></td>
    <td>Immutable</td>
    <td><pre>web3cli dropper-v1 deploy</pre></td>
    <td><pre>web3cli dropper-v1</pre></td>
    <td>n/a</td>
    <td><a href="./abi/Dropper.json"><pre>abi/Dropper.json</pre></a></td>
  </tr>
</table>

### Lootbox

Fully on-chain lootboxes that bundle together multiple tokens. These are implemented as Terminus tokens.
Lootboxes come in two varieties - deterministic and random.

Random lootboxes use decentralized, verifiable randomness to randomize the items that players receive when they open the lootbox.

<table>
  <tr>
    <th>Contract name</th>
    <th>Immutable or Upgradable</th>
    <th>Deployment</th>
    <th>CLI</th>
    <th>Solidity interface</th>
    <th>ABI</th>
  </tr>
  <tr>
    <td><a href="./contracts/Lootbox.sol"><pre>Lootbox</pre></a></td>
    <td>Immutable</td>
    <td><pre>web3cli lootbox deploy</pre></td>
    <td><pre>web3cli lootbox</pre></td>
    <td><a href="./contracts/interfaces/ILootbox.sol"><pre>ILootbox</pre></a></td>
    <td><a href="./abi/Lootbox.json"><pre>abi/Lootbox.json</pre></a></td>
  </tr>
</table>

### Crafting

A fully on-chain crafting mechanic. Administrators of this contract can create recipes - specifying inputs
and outputs.

Players can use those recipes by providing inputs in order to produce outputs.

<table>
  <tr>
    <th>Contract name</th>
    <th>Immutable or Upgradable</th>
    <th>Deployment</th>
    <th>CLI</th>
    <th>Solidity interface</th>
    <th>ABI</th>
  </tr>
  <tr>
    <td><a href="./contracts/crafting/facets/CraftingFacet.sol"><pre>CraftingFacet</pre></a></td>
    <td>Upgradable</td>
    <td><pre>web3cli core crafting-gogogo</pre></td>
    <td><pre>web3cli crafting</pre></td>
    <td><a href="./contracts/interfaces/ICrafting.sol"><pre>ICrafting</pre></a></td>
    <td><a href="./abi/CraftingFacet.json"><pre>abi/CraftingFacet.json</pre></a></td>
  </tr>
</table>

### Garden of Forking Paths

Garden of Forking Paths is a multiplayer choose your own adventure mechanic.

Players stake their NFTs into sessions on the Garden of Forking Paths contract. These NFTs can navigate through
different stages in their current session by choosing paths at each stage. They can earn different rewards
based on the paths they choose.

<table>
  <tr>
    <th>Contract name</th>
    <th>Immutable or Upgradable</th>
    <th>Deployment</th>
    <th>CLI</th>
    <th>Solidity interface</th>
    <th>ABI</th>
  </tr>
  <tr>
    <td><a href="./contracts/mechanics/garden-of-forking-paths/GardenOfForkingPaths.sol"><pre>GOFPFacet</pre></a></td>
    <td>Upgradable</td>
    <td><pre>web3cli core gofp-gogogo</pre></td>
    <td><pre>web3cli gofp</pre></td>
    <td><a href="./contracts/interfaces/IGOFP.sol"><pre>IGOFP</pre></a></td>
    <td><a href="./abi/GOFPFacet.json"><pre>abi/GOFPFacet.json</pre></a></td>
  </tr>
</table>

### Inventory

This implements a fully on-chain inventory system for ERC721 tokens. It allows ERC721 contracts to treat
the blockchain about the source of truth of the state of each token.

Administrators can define the inventory slots that an NFT collection (ERC721 contract) admits. They can
specify which items (ERC20 tokens, ERC721 tokens, ERC1155 tokens) are equippable in each slot.

NFT owners can equip and unequip valid items from each slot.

Games can use the items equipped in a character's inventory to determine their abilities in-game.

<table>
  <tr>
    <th>Contract name</th>
    <th>Immutable or Upgradable</th>
    <th>Deployment</th>
    <th>CLI</th>
    <th>Solidity interface</th>
    <th>ABI</th>
  </tr>
  <tr>
    <td><a href="./contracts/inventory/InventoryFacet.sol"><pre>InventoryFacet</pre></a></td>
    <td>Upgradable</td>
    <td><pre>web3cli core inventory-gogogo</pre></td>
    <td><pre>web3cli inventory</pre></td>
    <td><a href="./contracts/inventory/IInventory.sol"><pre>IInventory</pre></a></td>
    <td><a href="./abi/InventoryFacet.json"><pre>abi/InventoryFacet.json</pre></a></td>
  </tr>
</table>

### StatBlock

`StatBlock` is an on-chain registry for token stats/attributes. Games can publish attribute scores for
various tokens in their economy and these can be used by on-chain and off-chain mechanics to determine
the in-game properites of the in-game representations of those tokens.

<table>
  <tr>
    <th>Contract name</th>
    <th>Immutable or Upgradable</th>
    <th>Deployment</th>
    <th>CLI</th>
    <th>Solidity interface</th>
    <th>ABI</th>
  </tr>
  <tr>
    <td><a href="./contracts/stats/StatBlock.sol"><pre>StatBlock</pre></a></td>
    <td>Immutable</td>
    <td><pre>web3cli statblock deploy</pre></td>
    <td><pre>web3cli statblock</pre></td>
    <td><a href="./contracts/stats/IStatBlock.sol"><pre>IStatBlock</pre></a></td>
    <td><a href="./abi/StatBlock.json"><pre>abi/StatBlock.json</pre></a></td>
  </tr>
</table>

