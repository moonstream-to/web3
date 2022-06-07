// SPDX-License-Identifier: Apache-2.0

/**
 * Authors: Moonstream Engineering (engineering@moonstream.to)
 * GitHub: https://github.com/bugout-dev/dao

 */

pragma solidity ^0.8.0;

import {IDiamondCut} from "../../diamond/interfaces/IDiamondCut.sol";

library LibCrafting {
    bytes32 constant CRAFTING_STORAGE_POSITION =
        keccak256("moonstreamdao.eth.storage.crafting");

    uint256 constant ERC20_ITEM_TYPE = 20;
    uint256 constant ERC1155_ITEM_TYPE = 1155;

    struct CraftingItem {
        uint256 itemType; // item type: 20 for ERC20, 1155 for ERC1155
        address tokenAddress; // address of the token
        uint256 tokenId; // id of the token, any number for erc20
        uint256 amount; // amount of the token
    }

    struct Recipe {
        uint256 id;
        CraftingItem[] inputs;
        CraftingItem[] outputs;
    }

    struct CraftingStorage {
        address[] selectorToFacetAndPosition;
    }

    function craftingStorage()
        internal
        pure
        returns (CraftingStorage storage ds)
    {
        bytes32 position = CRAFTING_STORAGE_POSITION;
        assembly {
            ds.slot := position
        }
    }
}
