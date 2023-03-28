import { ethers } from "ethers"

import {
    CraftingRecipe,
    CraftingItem,
    CraftingInputActions,
    CraftingOutputActions,
    CraftingContract,
} from "./index"

async function main() {
    const rpcUrl = process.env.RPC_URL
    const privateKey = process.env.PRIVATE_KEY

    if (!rpcUrl) {
        throw new Error("RPC_URL env var is not set")
    }

    if (!privateKey) {
        throw new Error("PRIVATE_KEY env var is not set")
    }

    const provider = new ethers.providers.JsonRpcProvider(rpcUrl)

    const craftingContract = new CraftingContract(
        "0x8EA6A5EE9B9f7BCa384D804a12180473Ae4BE297",
        provider
    )

    const recipesCount = await craftingContract.numRecipes()
    console.log(`There are ${recipesCount} recipes on this contract`)
    for (let i = 1; i <= recipesCount.toNumber(); ++i) {
        console.log(JSON.stringify(await craftingContract.getRecipe(i)))
        console.log()
    }

    const signer = new ethers.Wallet(privateKey, provider)

    craftingContract.connect(signer)

    const emptyBottle: CraftingItem = {
        tokenAddress: "0x0000000000000000000000000000000000000000",
        amount: "1",
        tokenId: "1",
    }

    const milk: CraftingItem = {
        tokenAddress: "0x0000000000000000000000000000000000000000",
        amount: "100000000000000000000", // 100 * 10^18, 100 unim
    }

    const fullBottle: CraftingItem = {
        tokenAddress: "0x0000000000000000000000000000000000000000",
        amount: "1",
        tokenId: "2",
    }

    const bottlingRecipe: CraftingRecipe = {
        isActive: true,
        craftingInputs: [
            {
                item: emptyBottle,
                action: CraftingInputActions.BURN,
            },
            {
                item: milk,
                action: CraftingInputActions.TRANSFER,
            },
        ],
        craftingOutputs: [
            {
                item: fullBottle,
                action: CraftingOutputActions.MINT,
            },
        ],
    }
    console.log("Adding bottling contract")
    const recipeId = await craftingContract.addRecipe(bottlingRecipe)
    console.log(`Bottling recipe is created with id: ${recipeId}`)

    const unbottlingRecipe: CraftingRecipe = {
        isActive: true,
        craftingInputs: [
            {
                item: fullBottle,
                action: CraftingInputActions.BURN,
            },
        ],
        craftingOutputs: [
            {
                item: emptyBottle,
                action: CraftingOutputActions.MINT,
            },
            {
                item: milk,
                action: CraftingOutputActions.TRANSFER,
            },
        ],
    }

    console.log("Adding unbottling contract")
    const unbottlingRecipeId = await craftingContract.addRecipe(
        unbottlingRecipe
    )
    console.log(`Unbottling recipe is created with id: ${unbottlingRecipeId}`)
}

main().catch(console.error)
