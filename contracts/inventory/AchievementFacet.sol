// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {InventoryFacet, LibInventory} from "./InventoryFacet.sol";
import {Slot, EquippedItem} from "../interfaces/IInventory.sol";
import {ITerminus} from "../interfaces/ITerminus.sol";
import {LibTerminus} from "../terminus/LibTerminus.sol";
import {LibDiamondMoonstream} from "../diamond/libraries/LibDiamondMoonstream.sol";

import "@openzeppelin-contracts/contracts/token/ERC721/IERC721.sol";
import {ERC1155Receiver} from "@openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Receiver.sol";

library LibAchievement {
    bytes32 constant STORAGE_POSITION =
        keccak256("moonstreamdao.eth.storage.Achievement");

    struct AchievementStorage {
        // Execution permissions
        uint256 adminTerminusPoolID;
    }

    function achievementStorage()
        internal
        pure
        returns (AchievementStorage storage acs)
    {
        bytes32 position = STORAGE_POSITION;
        assembly {
            acs.slot := position
        }
    }
}

contract AchievementFacet is InventoryFacet {
    event AdminPrivilegeGranted(address indexed admin);
    event AdminPrivilegeRevoked(address indexed admin);

    function _enforceIsAdmin() internal view {
        ITerminus terminus = ITerminus(address(this));
        require(
            terminus.balanceOf(
                msg.sender,
                LibAchievement.achievementStorage().adminTerminusPoolID
            ) > 0,
            "AchievementFacet._enforceIsAdmin: not admin"
        );
    }

    function _checkIsAdmin(address maybeAdmin) internal view returns (bool) {
        ITerminus terminus = ITerminus(address(this));
        return
            terminus.balanceOf(
                maybeAdmin,
                LibAchievement.achievementStorage().adminTerminusPoolID
            ) > 0;
    }

    function initialize(address subjectAddress) external {
        LibDiamondMoonstream.enforceIsContractOwner();

        LibAchievement.AchievementStorage storage acs = LibAchievement
            .achievementStorage();

        // Set up executor pool
        ITerminus terminus = ITerminus(address(this));
        acs.adminTerminusPoolID = terminus.createPoolV1(
            type(uint256).max,
            false,
            true
        );
        terminus.setPaymentToken(address(0));
        terminus.setPoolBasePrice(0);

        // Copies `init` method from InventoryFacet - that is declared as an external method so cannot be
        // called directly here.
        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();
        istore.AdminTerminusAddress = address(this);
        istore.AdminTerminusPoolId = acs.adminTerminusPoolID;
        istore.ContractERC721Address = subjectAddress;

        // Slot 1 is unusable so that slot id will match pool id.
        istore.NumSlots += 1;
        uint256 newSlot = istore.NumSlots;
        // save the slot type!
        istore.SlotData[newSlot] = Slot({SlotURI: "", SlotIsPersistent: true});

        emit AdministratorDesignated(address(this), acs.adminTerminusPoolID);
        emit NewSubjectAddress(subjectAddress);
    }

    // Grants an account the role of admin.
    function grantAdminPrivilege(address admin) external {
        LibDiamondMoonstream.enforceIsContractOwner();

        LibAchievement.AchievementStorage storage acs = LibAchievement
            .achievementStorage();

        ITerminus terminus = ITerminus(address(this));

        if (terminus.balanceOf(admin, acs.adminTerminusPoolID) == 0) {
            terminus.mint(admin, acs.adminTerminusPoolID, 1, "");
        }

        emit AdminPrivilegeGranted(admin);
    }

    // Revokes the admin role from an account.
    function revokeAdminPrivilege(address admin) external {
        LibDiamondMoonstream.enforceIsContractOwner();

        LibAchievement.AchievementStorage storage acs = LibAchievement
            .achievementStorage();

        ITerminus terminus = ITerminus(address(this));

        uint256 balance = terminus.balanceOf(admin, acs.adminTerminusPoolID);
        if (balance > 0) {
            terminus.burn(admin, acs.adminTerminusPoolID, balance);
        }

        emit AdminPrivilegeRevoked(admin);
    }

    function createSlot(bool, string memory) public override returns (uint256) {
        revert("This method is disabled");
    }

    function markItemAsEquippableInSlot(
        uint256,
        uint256,
        address,
        uint256,
        uint256
    ) public override {
        revert("This method is disabled");
    }

    function createAchievementSlot(
        string memory metadataURI
    ) public returns (uint256) {
        _enforceIsAdmin();

        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();

        // Slots are 1-indexed!
        istore.NumSlots += 1;
        uint256 newSlot = istore.NumSlots;
        // save the slot type!
        istore.SlotData[newSlot] = Slot({
            SlotURI: metadataURI,
            SlotIsPersistent: true
        });

        // create terminus token
        ITerminus terminus = ITerminus(address(this));
        uint256 poolId = terminus.createPoolV2(
            type(uint256).max,
            false,
            true,
            metadataURI
        );

        require(
            newSlot == poolId,
            "AchievementFacet.createAchievementSlot: Slot id and pool id are mismatched."
        );

        // mark token equippable in slot
        istore.SlotEligibleItems[newSlot][LibInventory.ERC1155_ITEM_TYPE][
            address(this)
        ][poolId] = 1;

        emit ItemMarkedAsEquippableInSlot(
            newSlot,
            LibInventory.ERC1155_ITEM_TYPE,
            address(this),
            poolId,
            1
        );

        emit SlotCreated(msg.sender, newSlot);
        emit NewSlotURI(newSlot);
        emit NewSlotPersistence(newSlot, true);

        return newSlot;
    }

    function _mintToInventory(uint256 subjectTokenId, uint256 poolId) internal {
        LibInventory.InventoryStorage storage istore = LibInventory
            .inventoryStorage();

        // We could also revert the transaction and say the subject already has this achievement. Or we
        // could do nothing and assume the achievement is correctly appplied already.
        if (
            istore
            .EquippedItems[istore.ContractERC721Address][subjectTokenId][poolId]
                .ItemType != 0
        ) {
            _unequip(subjectTokenId, poolId, true, 0);
        }

        ITerminus terminus = ITerminus(address(this));
        terminus.mint(address(this), poolId, 1, "");

        istore.EquippedItems[istore.ContractERC721Address][subjectTokenId][
            poolId
        ] = EquippedItem({
            ItemType: LibInventory.ERC1155_ITEM_TYPE,
            ItemAddress: address(this),
            ItemTokenId: poolId,
            Amount: 1
        });

        emit ItemEquipped(
            subjectTokenId,
            poolId,
            LibInventory.ERC1155_ITEM_TYPE,
            address(this),
            poolId,
            1,
            msg.sender
        );
    }

    function adminBatchMintToInventory(
        uint256[] memory subjectTokenIds,
        uint256[] memory poolIds
    ) public {
        _enforceIsAdmin();

        require(
            subjectTokenIds.length == poolIds.length,
            "AchievementFacet.adminBatchMintToInventory: subjectTokenIds and poolIds length mismatch"
        );

        uint256 i = 0;
        for (i = 0; i < subjectTokenIds.length; i++) {
            _mintToInventory(subjectTokenIds[i], poolIds[i]);
        }
    }
}
