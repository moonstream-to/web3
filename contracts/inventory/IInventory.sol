// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

struct Slot {
    string SlotURI;
    bool SlotIsPersistent;
}

// EquippedItem represents an item equipped in a specific inventory slot for a specific ERC721 token.
struct EquippedItem {
    uint256 ItemType;
    address ItemAddress;
    uint256 ItemTokenId;
    uint256 Amount;
}

interface IInventory {
    event AdministratorDesignated(
        address indexed adminTerminusAddress,
        uint256 indexed adminTerminusPoolId
    );

    event ContractAddressDesignated(address indexed contractAddress);

    event SlotCreated(
        address indexed creator,
        uint256 indexed slot,
        bool persistent
    );

    event ItemMarkedAsEquippableInSlot(
        uint256 indexed slot,
        uint256 indexed itemType,
        address indexed itemAddress,
        uint256 itemPoolId,
        uint256 maxAmount
    );

    event NewSlotURI(uint256 indexed slotId);

    event ItemEquipped(
        uint256 indexed subjectTokenId,
        uint256 indexed slot,
        uint256 itemType,
        address indexed itemAddress,
        uint256 itemTokenId,
        uint256 amount,
        address equippedBy
    );

    event ItemUnequipped(
        uint256 indexed subjectTokenId,
        uint256 indexed slot,
        uint256 itemType,
        address indexed itemAddress,
        uint256 itemTokenId,
        uint256 amount,
        address unequippedBy
    );

    function adminTerminusInfo() external view returns (address, uint256);

    function subject() external view returns (address);

    // Cosntraint: Admin
    function createSlot(
        bool persistent,
        string memory slotURI
    ) external returns (uint256);

    function numSlots() external view returns (uint256);

    function slotIsPersistent(uint256 slotId) external view returns (bool);

    // Cosntraint: Admin
    function markItemAsEquippableInSlot(
        uint256 slot,
        uint256 itemType,
        address itemAddress,
        uint256 itemPoolId,
        uint256 maxAmount
    ) external;

    function maxAmountOfItemInSlot(
        uint256 slot,
        uint256 itemType,
        address itemAddress,
        uint256 itemPoolId
    ) external view returns (uint256);

    // Constraint: Non-reentrant.
    function equip(
        uint256 subjectTokenId,
        uint256 slot,
        uint256 itemType,
        address itemAddress,
        uint256 itemTokenId,
        uint256 amount
    ) external;

    // Constraint: Non-reentrant.
    function unequip(
        uint256 subjectTokenId,
        uint256 slot,
        bool unequipAll,
        uint256 amount
    ) external;

    function getEquippedItem(
        uint256 subjectTokenId,
        uint256 slot
    ) external view returns (EquippedItem memory item);

    function getSlotById(
        uint256 slotId
    ) external view returns (Slot memory slots);

    function getSlotURI(uint256 slotId) external view returns (string memory);

    // Cosntraint: Admin
    function setSlotPersistent(uint256 slotId, bool persistent) external;
}
