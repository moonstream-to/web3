// SPDX-License-Identifier: MIT

/**
 * Authors: Omar Garcia<ogarciarevett>
 * https://github.com/lootledger/inventory
 */

pragma solidity ^0.8.17;

import "@openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Holder.sol";
import "@openzeppelin-contracts/contracts/token/ERC721/utils/ERC721Holder.sol";
import "@openzeppelin-contracts/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin-contracts/contracts/token/ERC1155/IERC1155.sol";
import "@openzeppelin-contracts/contracts/utils/Context.sol";
import {DiamondReentrancyGuard} from "../diamond/security/DiamondReentrancyGuard.sol";
import "../diamond/libraries/LibDiamond.sol";
import "../libraries/LibInventory.sol";
import "../interfaces/IInventory.sol";

contract InventoryFacet is
    IInventory,
    ERC721Holder,
    ERC1155Holder,
    DiamondReentrancyGuard,
    Context
{
    modifier onlyAdmin() {
        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();
        require(
            istore.AdminAddress == _msgSender(),
            "Only Admin address allowed"
        );
        _;
    }

    modifier requireValidItemType(uint256 itemType) {
        require(
            itemType == LibInventory.ERC20_ITEM_TYPE ||
                itemType == LibInventory.ERC721_ITEM_TYPE ||
                itemType == LibInventory.ERC1155_ITEM_TYPE,
            "InventoryFacet.requireValidItemType: Invalid item type"
        );
        _;
    }

    function init(address adminAddress, address contractAddress) external {
        LibDiamond.enforceIsContractOwner();
        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();
        istore.AdminAddress = adminAddress;
        istore.ContractERC721Address = contractAddress;

        emit AdministratorDesignated(adminAddress);
        emit ContractAddressDesignated(contractAddress);
    }

    function adminInfo() external view returns (address) {
        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();
        return (istore.AdminAddress);
    }

    function subject() external view returns (address) {
        return LibInventory.inventoryStorage().ContractERC721Address;
    }

    function createSlot(
        bool isPersistent,
        string memory slotURI
    ) external onlyAdmin returns (uint256) {
        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();

        istore.NumSlots += 1;
        uint256 newSlot = istore.NumSlots;
        istore.SlotData[newSlot] = LibInventory.Slot({
            SlotURI: slotURI,
            SlotIsPersistent: isPersistent,
            SlotId: newSlot
        });

        emit SlotCreated(_msgSender(), newSlot);
        return newSlot;
    }

    function numSlots() external view returns (uint256) {
        return LibInventory.inventoryStorage().NumSlots;
    }

    function getSlotById(
        uint256 slotId
    ) external view returns (LibInventory.Slot memory slot) {
        return LibInventory.inventoryStorage().SlotData[slotId];
    }

    function setSlotURI(
        string memory newSlotURI,
        uint256 slotId
    ) external onlyAdmin {
        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();

        LibInventory.Slot memory slot = istore.SlotData[slotId];
        slot.SlotURI = newSlotURI;
        istore.SlotData[slotId] = slot;
        emit NewSlotURI(slotId);
    }

    function setSlotPersistent(
        uint256 slotId,
        bool isPersistent
    ) external onlyAdmin {
        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();

        LibInventory.Slot memory slot = istore.SlotData[slotId];
        slot.SlotIsPersistent = isPersistent;
        istore.SlotData[slotId] = slot;
    }

    function markItemAsEquippableInSlot(
        uint256 slot,
        uint256 itemType,
        address itemAddress,
        uint256 itemTokenId,
        uint256 maxAmount
    ) external onlyAdmin requireValidItemType(itemType) {
        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();

        require(
            itemType == LibInventory.ERC1155_ITEM_TYPE || itemTokenId == 0,
            "InventoryFacet.markItemAsEquippableInSlot: Token ID can only be non-zero for items from ERC1155 contracts"
        );
        require(
            itemType != LibInventory.ERC721_ITEM_TYPE || maxAmount <= 1,
            "InventoryFacet.markItemAsEquippableInSlot: maxAmount should be at most 1 for items from ERC721 contracts"
        );

        istore.SlotEligibleItems[slot][itemType][itemAddress][
            itemTokenId
        ] = maxAmount;

        emit ItemMarkedAsEquippableInSlot(
            slot,
            itemType,
            itemAddress,
            itemTokenId,
            maxAmount
        );
    }

    function _unequip(
        uint256 subjectTokenId,
        uint256 slot,
        bool unequipAll,
        uint256 amount
    ) internal {
        require(
            !unequipAll || amount == 0,
            "InventoryFacet._unequip: Set amount to 0 if you are unequipping all instances of the item in that slot"
        );

        require(
            unequipAll || amount > 0,
            "InventoryFacet._unequip: Since you are not unequipping all instances of the item in that slot, you must specify how many instances you want to unequip"
        );

        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();

        require(
            istore.SlotData[slot].SlotIsPersistent,
            "InventoryFacet._unequip: That slot is not unequippable"
        );

        LibInventory.EquippedItem storage existingItem = istore.EquippedItems[
            istore.ContractERC721Address
        ][subjectTokenId][slot];

        if (unequipAll) {
            amount = existingItem.Amount;
        }

        require(
            amount <= existingItem.Amount,
            "InventoryFacet._unequip: Attempting to unequip too many items from the slot"
        );

        if (existingItem.ItemType == 20) {
            IERC20 erc20Contract = IERC20(existingItem.ItemAddress);
            bool transferSuccess = erc20Contract.transfer(_msgSender(), amount);
            require(
                transferSuccess,
                "InventoryFacet._unequip: Error unequipping ERC20 item - transfer was unsuccessful"
            );
        } else if (existingItem.ItemType == 721 && amount > 0) {
            IERC721 erc721Contract = IERC721(existingItem.ItemAddress);
            erc721Contract.safeTransferFrom(
                address(this),
                _msgSender(),
                existingItem.ItemTokenId
            );
        } else if (existingItem.ItemType == 1155) {
            IERC1155 erc1155Contract = IERC1155(existingItem.ItemAddress);
            erc1155Contract.safeTransferFrom(
                address(this),
                _msgSender(),
                existingItem.ItemTokenId,
                amount,
                ""
            );
        }

        emit ItemUnequipped(
            subjectTokenId,
            slot,
            existingItem.ItemType,
            existingItem.ItemAddress,
            existingItem.ItemTokenId,
            amount,
            _msgSender()
        );

        existingItem.Amount -= amount;
        if (existingItem.Amount == 0) {
            delete istore.EquippedItems[istore.ContractERC721Address][
                subjectTokenId
            ][slot];
        }
    }

    function equip(
        uint256 subjectTokenId,
        uint256 slot,
        uint256 itemType,
        address itemAddress,
        uint256 itemTokenId,
        uint256 amount
    ) public requireValidItemType(itemType) diamondNonReentrant {
        require(
            itemType == LibInventory.ERC721_ITEM_TYPE ||
                itemType == LibInventory.ERC1155_ITEM_TYPE ||
                itemTokenId == 0,
            "InventoryFacet.equip: itemTokenId can only be non-zero for ERC721 or ERC1155 items"
        );

        require(
            itemType == LibInventory.ERC20_ITEM_TYPE ||
                itemType == LibInventory.ERC1155_ITEM_TYPE ||
                amount == 1,
            "InventoryFacet.equip: amount can be other value than 1 only for ERC20 and ERC1155 items"
        );

        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();

        IERC721 subjectContract = IERC721(istore.ContractERC721Address);

        require(
            _msgSender() == subjectContract.ownerOf(subjectTokenId),
            "InventoryFacet.equip: Message sender is not owner of subject token"
        );

        if (
            istore
            .EquippedItems[istore.ContractERC721Address][subjectTokenId][slot]
                .ItemType != 0
        ) {
            _unequip(subjectTokenId, slot, true, 0);
        }

        require(
            istore.SlotEligibleItems[slot][itemType][itemAddress][
                itemType == 1155 ? itemTokenId : 0
            ] >= amount,
            "InventoryFacet.equip: You can not equip those many instances of that item into the given slot"
        );

        if (itemType == LibInventory.ERC20_ITEM_TYPE) {
            IERC20 erc20Contract = IERC20(itemAddress);
            bool erc20TransferSuccess = erc20Contract.transferFrom(
                _msgSender(),
                address(this),
                amount
            );
            require(
                erc20TransferSuccess,
                "InventoryFacet.equip: Error equipping ERC20 item - transfer was unsuccessful"
            );
        } else if (itemType == LibInventory.ERC721_ITEM_TYPE) {
            IERC721 erc721Contract = IERC721(itemAddress);
            require(
                _msgSender() == erc721Contract.ownerOf(itemTokenId),
                "InventoryFacet.equip: Message sender cannot equip an item that they do not own"
            );
            erc721Contract.safeTransferFrom(
                _msgSender(),
                address(this),
                itemTokenId
            );
        } else if (itemType == LibInventory.ERC1155_ITEM_TYPE) {
            IERC1155 erc1155Contract = IERC1155(itemAddress);
            require(
                erc1155Contract.balanceOf(_msgSender(), itemTokenId) >= amount,
                "InventoryFacet.equip: Message sender does not own enough of that item to equip"
            );
            erc1155Contract.safeTransferFrom(
                _msgSender(),
                address(this),
                itemTokenId,
                amount,
                ""
            );
        }

        emit ItemEquipped(
            subjectTokenId,
            slot,
            itemType,
            itemAddress,
            itemTokenId,
            amount,
            _msgSender()
        );

        istore.EquippedItems[istore.ContractERC721Address][subjectTokenId][
            slot
        ] = LibInventory.EquippedItem({
            ItemType: itemType,
            ItemAddress: itemAddress,
            ItemTokenId: itemTokenId,
            Amount: amount
        });
    }

    function getAllEquippedItems(
        uint256 subjectTokenId
    ) external view returns (LibInventory.EquippedItem[] memory equippedItems) {
        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();
        uint256 totalSlots = this.numSlots();

        LibInventory.EquippedItem[]
            memory items = new LibInventory.EquippedItem[](totalSlots);

        uint256 counter = 0;

        for (uint256 i = 0; i < totalSlots; i++) {
            LibInventory.EquippedItem memory equippedItemBlock = istore
                .EquippedItems[istore.ContractERC721Address][subjectTokenId][i];
            if (
                equippedItemBlock.ItemType != 0 ||
                equippedItemBlock.ItemAddress != address(0) ||
                equippedItemBlock.Amount != 0
            ) {
                items[counter] = equippedItemBlock;
                counter++;
            }
        }

        LibInventory.EquippedItem[]
            memory fixedEquippedItems = new LibInventory.EquippedItem[](
                counter
            );

        for (uint256 i = 0; i < counter; i++) {
            fixedEquippedItems[i] = items[i];
        }

        return fixedEquippedItems;
    }

    function getEquippedItem(
        uint256 subjectTokenId,
        uint256 slot
    ) external view returns (LibInventory.EquippedItem memory equippedItem) {
        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();
        return
            istore.EquippedItems[istore.ContractERC721Address][subjectTokenId][
                slot
            ];
    }

    function equipBatch(
        uint256 subjectTokenId,
        uint256[] memory slots,
        LibInventory.EquippedItem[] memory items
    ) external {
        require(
            items.length > 0,
            "InventoryFacet.batchEquip: Must equip at least one item"
        );
        require(
            slots.length == items.length,
            "InventoryFacet.batchEquip: Must provide a slot for each item"
        );

        for (uint256 i = 0; i < items.length; i++) {
            equip(
                subjectTokenId,
                slots[i],
                items[i].ItemType,
                items[i].ItemAddress,
                items[i].ItemTokenId,
                items[i].Amount
            );
        }
    }

    function getSlotURI(uint256 slotId) external view returns (string memory) {
        return LibInventory.inventoryStorage().SlotData[slotId].SlotURI;
    }

    function slotIsPersistent(
        uint256 slotId
    ) external view override returns (bool) {
        return
            LibInventory.inventoryStorage().SlotData[slotId].SlotIsPersistent;
    }

    function maxAmountOfItemInSlot(
        uint256 slot,
        uint256 itemType,
        address itemAddress,
        uint256 itemTokenId
    ) external view returns (uint256) {
        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();
        return
            istore.SlotEligibleItems[slot][itemType][itemAddress][itemTokenId];
    }
}
