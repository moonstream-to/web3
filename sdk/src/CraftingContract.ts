import { ethers } from "ethers"
import { CraftingFacet__factory } from "./contract-types"
import { CraftingFacet } from "./contract-types"
import { PromiseOrValue } from "./contract-types/common"
import {
    CraftingInputItemStruct,
    CraftingOutputItemStruct,
    RecipeStruct,
} from "./contract-types/CraftingFacet"
import {
    CraftingRecipe,
    CraftingInputActions,
    CraftingOutputActions,
    ERC1155Item,
    CraftingInput,
    CraftingOutput,
} from "./types/CraftingTypes"

export class CraftingContract {
    public contract: CraftingFacet
    public signer?: ethers.Signer = undefined
    constructor(
        public address: string,
        public provider: ethers.providers.Provider
    ) {
        this.contract = CraftingFacet__factory.connect(address, provider)
    }

    public async _getRecipeRaw(recipeId: PromiseOrValue<ethers.BigNumberish>) {
        return this.contract.getRecipe(recipeId)
    }

    public async getRecipe(
        recipeId: PromiseOrValue<ethers.BigNumberish>
    ): Promise<CraftingRecipe> {
        let rawRecipe = await this.contract.getRecipe(recipeId)
        let craftingInputs: Array<CraftingInput> = rawRecipe.inputs.map(
            (el): CraftingInput => {
                let action =
                    el.tokenAction.toNumber() as unknown as CraftingInputActions
                if (el.tokenType.toString() === "20") {
                    return {
                        action: action,
                        item: {
                            tokenAddrress: el.tokenAddress,
                            amount: el.amount.toString(),
                        },
                    }
                } else {
                    return {
                        action: action,
                        item: {
                            tokenId: el.tokenId.toString(),
                            tokenAddrress: el.tokenAddress,
                            amount: el.amount.toString(),
                        },
                    }
                }
            }
        )
        let craftingOutputs = rawRecipe.outputs.map((el): CraftingOutput => {
            let action =
                el.tokenAction.toNumber() as unknown as CraftingOutputActions
            if (el.tokenType.toString() === "20") {
                return {
                    action: action,
                    item: {
                        tokenAddrress: el.tokenAddress,
                        amount: el.amount.toString(),
                    },
                }
            } else {
                return {
                    action: action,
                    item: {
                        tokenAddrress: el.tokenAddress,
                        amount: el.amount.toString(),
                        tokenId: el.tokenId.toString(),
                    },
                }
            }
        })

        return {
            isActive: rawRecipe.isActive,
            craftingInputs: craftingInputs,
            craftingOutputs: craftingOutputs,
        }
    }

    public async numRecipes(): Promise<ethers.BigNumber> {
        return this.contract.numRecipes()
    }

    public async craft(
        recipeId: PromiseOrValue<ethers.BigNumberish>
    ): Promise<ethers.ContractTransaction> {
        return this.contract.craft(recipeId)
    }

    public async addRecipe(recipe: CraftingRecipe): Promise<ethers.BigNumber> {
        const craftingInputs = recipe.craftingInputs.map(
            (el): CraftingInputItemStruct => ({
                tokenType: "tokenId" in el.item ? 1155 : 20,
                tokenAddress: el.item.tokenAddrress,
                tokenId:
                    "tokenId" in el.item ? (el.item as ERC1155Item).tokenId : 0,
                amount: el.item.amount,
                tokenAction: el.action,
            })
        )
        const craftingOutputs = recipe.craftingOutputs.map(
            (el): CraftingOutputItemStruct => ({
                tokenType: "tokenId" in el.item ? 1155 : 20,
                tokenAddress: el.item.tokenAddrress,
                tokenId:
                    "tokenId" in el.item ? (el.item as ERC1155Item).tokenId : 0,
                amount: el.item.amount,
                tokenAction: el.action,
            })
        )
        const recipeStruct: RecipeStruct = {
            inputs: craftingInputs,
            outputs: craftingOutputs,
            isActive: recipe.isActive,
        }
        const tx = await this.contract.addRecipe(recipeStruct)
        await tx.wait(1)
        return this.numRecipes()
    }
    public connect(_signer: ethers.Signer) {
        this.signer = _signer
        this.contract = this.contract.connect(this.signer)
    }
}
