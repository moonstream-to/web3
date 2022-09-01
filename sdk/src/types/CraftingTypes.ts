export interface ERC20Item {
    tokenAddrress: string
    amount: string
}

export interface ERC1155Item {
    tokenAddrress: string
    tokenId: string
    amount: string
}

export interface CraftingRecipe {
    isActive: boolean
    craftingInputs: Array<CraftingInput>
    craftingOutputs: Array<CraftingOutput>
}

export interface CraftingInput {
    item: CraftingItem
    action: CraftingInputActions
}

export interface CraftingOutput {
    item: CraftingItem
    action: CraftingOutputActions
}

export enum CraftingInputActions {
    TRANSFER = 0,
    BURN = 1,
    HOLD = 2,
}

export enum CraftingOutputActions {
    TRANSFER = 0,
    MINT = 1,
}

export type CraftingItem = ERC20Item | ERC1155Item
