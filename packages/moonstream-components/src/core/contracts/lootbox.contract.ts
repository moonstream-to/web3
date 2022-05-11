import { Lootbox } from "../../../../../types/contracts/Lootbox";
const lootboxAbi = require("../../../../../abi/Lootbox.json");
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";

export const getLootboxState = (address: any, ctx: MoonstreamWeb3ProviderInterface, lootboxId: number) => async () => {
    const web3 = ctx.web3;
    const lootbox = new web3.eth.Contract(lootboxAbi) as any as Lootbox;
    lootbox.options.address = address;

    const lootboxUri = await lootbox.methods.getLootboxURI(lootboxId).call();
    const lootboxBalance = await lootbox.methods.getLootboxBalance(lootboxId, ctx.account).call();

    return { lootboxUri, lootboxBalance };
};

