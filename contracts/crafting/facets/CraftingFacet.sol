// SPDX-License-Identifier: Apache-2.0

/**
 * Authors: Moonstream Engineering (engineering@moonstream.to)
 * GitHub: https://github.com/bugout-dev/dao
 */

pragma solidity ^0.8.0;
import "@openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin-contracts/contracts/token/ERC20/presets/ERC20PresetMinterPauser.sol";
import "@openzeppelin-contracts/contracts/token/ERC1155/extensions/ERC1155Burnable.sol";
import "@openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Burnable.sol";
import "@openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Holder.sol";
import "@openzeppelin-contracts/contracts/token/ERC721/utils/ERC721Holder.sol";
import {MockTerminus} from "../../mock/MockTerminus.sol";
import {MockErc20} from "../../mock/MockErc20.sol";
import "../libraries/LibCrafting.sol";
import "../../diamond/libraries/LibDiamond.sol";
import "../../diamond/security/DiamondReentrancyGuard.sol";

contract CraftingFacet is ERC1155Holder, ERC721Holder, DiamondReentrancyGuard {
    function addRecipe(Recipe calldata recipe) public {
        LibCrafting.CraftingStorage storage cs = LibCrafting.craftingStorage();
        cs.numRecipes++;
        cs.recipes[cs.numRecipes] = recipe;
    }

    function getRecipe(uint256 recipeId) public view returns (Recipe memory) {
        return LibCrafting.craftingStorage().recipes[recipeId];
    }

    function numRecipes() public view returns (uint256) {
        return LibCrafting.craftingStorage().numRecipes;
    }

    function craft(uint256 recipeId) public diamondNonReentrant {
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
                        revert("User doesn't hold enough tokens for crafting");
                    }
                }
            } else if (
                recipe.inputs[i].tokenType == LibCrafting.ERC1155_TOKEN_TYPE
            ) {
                ERC1155Burnable token = ERC1155Burnable(
                    recipe.inputs[i].tokenAddress
                );
                if (
                    recipe.inputs[i].tokenAction ==
                    LibCrafting.INPUT_TOKEN_ACTION_TRANSFER
                ) {
                    token.safeTransferFrom(
                        msg.sender,
                        address(this),
                        recipe.inputs[i].tokenId,
                        recipe.inputs[i].amount,
                        ""
                    );
                } else if (
                    recipe.inputs[i].tokenAction ==
                    LibCrafting.INPUT_TOKEN_ACTION_BURN
                ) {
                    token.burn(
                        msg.sender,
                        recipe.inputs[i].tokenId,
                        recipe.inputs[i].amount
                    );
                } else if (
                    recipe.inputs[i].tokenAction ==
                    LibCrafting.INPUT_TOKEN_ACTION_HOLD
                ) {
                    uint256 balance = token.balanceOf(
                        msg.sender,
                        recipe.inputs[i].tokenId
                    );
                    if (balance < recipe.inputs[i].amount) {
                        revert("User doesn't hold enough tokens for crafting");
                    }
                }
            }
        }

        for (uint256 i = 0; i < recipe.outputs.length; i++) {
            if (recipe.outputs[i].tokenType == LibCrafting.ERC20_TOKEN_TYPE) {
                MockErc20 token = MockErc20(recipe.outputs[i].tokenAddress);
                if (
                    recipe.outputs[i].tokenAction ==
                    LibCrafting.OUTPUT_TOKEN_ACTION_TRANSFER
                ) {
                    token.transfer(msg.sender, recipe.outputs[i].amount);
                } else if (
                    recipe.outputs[i].tokenAction ==
                    LibCrafting.OUTPUT_TOKEN_ACTION_MINT
                ) {
                    token.mint(msg.sender, recipe.outputs[i].amount);
                }
            } else if (
                recipe.outputs[i].tokenType == LibCrafting.ERC1155_TOKEN_TYPE
            ) {
                MockTerminus token = MockTerminus(
                    recipe.outputs[i].tokenAddress
                );
                if (
                    recipe.outputs[i].tokenAction ==
                    LibCrafting.OUTPUT_TOKEN_ACTION_TRANSFER
                ) {
                    token.safeTransferFrom(
                        address(this),
                        msg.sender,
                        recipe.outputs[i].tokenId,
                        recipe.outputs[i].amount,
                        ""
                    );
                } else if (
                    recipe.outputs[i].tokenAction ==
                    LibCrafting.OUTPUT_TOKEN_ACTION_MINT
                ) {
                    token.mint(
                        msg.sender,
                        recipe.outputs[i].tokenId,
                        recipe.outputs[i].amount,
                        ""
                    );
                }
            }
        }
    }
}
