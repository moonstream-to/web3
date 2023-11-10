// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/**
LibInventory defines the storage structure used by the Inventory contract as a facet for an EIP-2535 Diamond
proxy.
 */
library LibInventory {
  bytes32 constant STORAGE_POSITION = keccak256("eth.storage.Inventory");

  uint256 constant ERC20_ITEM_TYPE = 20;
  uint256 constant ERC721_ITEM_TYPE = 721;
  uint256 constant ERC1155_ITEM_TYPE = 1155;

  struct Slot {
    string SlotURI;
    bool SlotIsPersistent;
    uint256 SlotId;
  }

  // EquippedItem represents an item equipped in a specific inventory slot for a specific ERC721 token.
  struct EquippedItem {
    uint256 ItemType;
    address ItemAddress;
    uint256 ItemTokenId;
    uint256 Amount;
  }

  struct InventoryStorage {
    address AdminAddress;
    address ContractERC721Address;
    uint256 NumSlots;
    // SlotId => slot, useful to get the rest of the slot data.
    mapping(uint256 => Slot) SlotData;

    // Slot => item type => item address => item token ID => maximum equippable
    // For ERC20 and ERC721 tokens, item token ID is assumed to be 0. No data will be stored under positive
    // item token IDs.
    //
    // NOTE: It is possible for the same contract to implement multiple of these ERCs (e.g. ERC20 and ERC721),
    // so this data structure actually makes sense.
    mapping(uint256 => mapping(uint256 => mapping(address => mapping(uint256 => uint256)))) SlotEligibleItems;
    // Subject contract address => subject token ID => slot => EquippedItem
    // Item type and Pool ID on EquippedItem have the same constraints as they do elsewhere (e.g. in SlotEligibleItems).
    //
    // NOTE: We have added the subject contract address as the first mapping key as a defense against
    // future modifications which may allow administrators to modify the subject contract address.
    // If such a modification were made, it could make it possible for a bad actor administrator
    // to change the address of the subject token to the address to an ERC721 contract they control
    // and drain all items from every subject token's inventory.
    // If this contract is deployed as a Diamond proxy, the owner of the Diamond can pretty much
    // do whatever they want in any case, but adding the subject contract address as a key protects
    // users of non-Diamond deployments even under small variants of the current implementation.
    // It also offers *some* protection to users of Diamond deployments of the Inventory.
    // ERC721 Contract Address =>
    // subjectTokenId =>
    // slotId =>
    // EquippedItem struct
    mapping(address => mapping(uint256 => mapping(uint256 => EquippedItem))) EquippedItems;
  }

  function inventoryStorage() internal pure returns (InventoryStorage storage istore) {
    bytes32 position = STORAGE_POSITION;
    assembly {
      istore.slot := position
    }
  }
}
