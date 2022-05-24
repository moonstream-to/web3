import { toNumber } from "web3-utils";
import { Lootbox } from "../../../../../types/contracts/Lootbox";
const lootboxAbi = require("../../../../../abi/Lootbox.json");
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";

export const lootboxContract = (
  contractAddress: string,
  ctx: MoonstreamWeb3ProviderInterface
): Lootbox => {
  const web3 = ctx.web3;
  const contract = new web3.eth.Contract(lootboxAbi) as any as Lootbox;
  contract.options.address = contractAddress;
  return contract;
};

export const getLootboxTokenState =
  (address: any, ctx: MoonstreamWeb3ProviderInterface, lootboxId: number) =>
  async () => {
    const lootbox = lootboxContract(address, ctx);

    const lootboxUri = await lootbox.methods.getLootboxURI(lootboxId).call();
    const lootboxBalance = await lootbox.methods
      .getLootboxBalance(lootboxId, ctx.account)
      .call();

    return { lootboxUri, lootboxBalance };
  };

export const getLootboxState =
  (address: any, ctx: MoonstreamWeb3ProviderInterface) => async () => {
    const lootbox = lootboxContract(address, ctx);

    const lootboxesCount = await lootbox.methods.totalLootboxCount().call();

    const lootboxIds = Array.from(
      { length: toNumber(lootboxesCount) },
      (_, index) => index + 1
    );
    const activeOpening = await getActiveOpening(address, ctx);

    return { lootboxIds, activeOpening };
  };

export const getActiveOpening = async (
  contractAddress: any,
  ctx: MoonstreamWeb3ProviderInterface
) => {
  const lootbox = lootboxContract(contractAddress, ctx) as any as Lootbox;
  const requestHash = await lootbox.methods
    //eslint-disable-next-line
    .CurrentOpeningforUser(ctx.account)
    .call();
  console.log("requestHash", requestHash);
  if (
    requestHash ===
    "0x0000000000000000000000000000000000000000000000000000000000000000"
  ) {
    console.log("no active opening");
    return null;
  }
  const opening = await lootbox.methods
    //eslint-disable-next-line
    .ActiveLootboxOpenings(requestHash)
    .call();
  console.log("opening", opening);
  return {
    lootboxId: opening.lootboxId,
    isReadyToComplete: opening.status === "2",
  };
};
