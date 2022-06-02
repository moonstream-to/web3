// SPDX-License-Identifier: Apache-2.0

/**
 * Authors: Moonstream Engineering (engineering@moonstream.to)
 * GitHub: https://github.com/bugout-dev/dao
 */

pragma solidity ^0.8.0;
import "@openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin-contracts/contracts/token/ERC1155/IERC1155.sol";
import "@openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Holder.sol";

import "../libraries/LibCrafting.sol";
import "../../diamond/libraries/LibDiamond.sol";

contract Craftting {
    function addRecipe(Recipe memory recipe) public {
        LibCrafting.CraftingStorage storage cs = LibCrafting.craftingStorage();
        cs.numRecipes++;
        cs.recipes[cs.numRecipes] = recipe;
    }

    function getRecipe(uint256 recipeId) public view returns (Recipe memory) {
        return LibCrafting.craftingStorage().recipes[recipeId];
    }

    function craft(uint256 recipeId) public {
        Recipe memory recipe = LibCrafting.craftingStorage().recipes[recipeId];
        for (uint256 i = 0; i < recipe.inputs.length; i++) {
            if (recipe.inputs[i].tokenType == LibCrafting.ERC20_TOKEN_TYPE) {
                ERC20Burnable token = ERC20Burnable(
                    recipe.inputs[i].tokenAddress
                );
                if (
                    recipe.inputs[i].tokenAction ==
                    LibCrafting.INPUT_TOKEN_ACTION_TRANSFER
                ) {
                    token.transferFrom(
                        msg.sender,
                        address(this),
                        recipe.inputs[i].amount
                    );
                } else if (
                    recipe.inputs[i].tokenAction ==
                    LibCrafting.INPUT_TOKEN_ACTION_BURN
                ) {
                    token.burnFrom(msg.sender, recipe.inputs[i].amount);
                } else if (
                    recipe.inputs[i].tokenAction ==
                    LibCrafting.INPUT_TOKEN_ACTION_HOLD
                ) {
                    uint256 balance = token.balanceOf(msg.sender);
                    if (balance < recipe.inputs[i].amount) {
                        revert(
                            "User doesn't hold enough token to crawl tokens"
                        );
                    }
                }
            } else if (
                recipe.inputs[i].tokenType == LibCrafting.ERC1155_TOKEN_TYPE
            ) {
                IERC1155 token = IERC1155(recipe.inputs[i].tokenAddress);
            }
        }
    }
}
