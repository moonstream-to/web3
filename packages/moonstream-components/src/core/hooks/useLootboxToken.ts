import { useQuery } from "react-query";

import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";
import { useToast } from ".";
import {
  getLootboxTokenState,
  lootboxContract,
  getActiveOpening,
} from "../contracts/lootbox.contract";

const useLootboxToken = ({
  contractAddress,
  lootboxId,
  ctx,
}: {
  contractAddress: string;
  lootboxId: number;
  ctx: MoonstreamWeb3ProviderInterface;
}) => {
  const toast = useToast();

  const state = useQuery(
    ["LootboxTokenState", contractAddress, ctx.targetChain?.chainId, lootboxId],
    () => getLootboxTokenState(contractAddress, ctx, lootboxId)(),
    {
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) &&
        !!ctx.chainId &&
        ctx.chainId === ctx.targetChain?.chainId,
    }
  );

  const lootbox = lootboxContract(contractAddress, ctx);

  const _openLootbox = async (lootboxId: number, count: number) => {
    const lootboxBalance = await lootbox.methods
      .getLootboxBalance(lootboxId, ctx.account)
      .call();
    if (parseInt(lootboxBalance) < count) {
      toast("You don't have enough lootboxes", "error");
      return;
    }
    toast("Opening lootbox");
    const lootboxType = await lootbox.methods
      .lootboxTypebyLootboxId(lootboxId)
      .call();
    if (lootboxType === "0") {
      console.log("opening ordinary lootbox");
      await lootbox.methods
        .openLootbox(lootboxId, count)
        .send({ from: ctx.account });
    } else if (lootboxType === "1") {
      console.log("opening random lootbox");
      const opening = await getActiveOpening(contractAddress, ctx);
      if (opening !== null) {
        toast("You already have an active opening", "error");
        return;
      }
      if (count > 1) {
        toast("You can only open one random lootbox at a time", "error");
        return;
      }
      await lootbox.methods
        .openLootbox(lootboxId, count)
        .send({ from: ctx.account });
    }
  };

  const _completeLootboxOpening = async () => {
    const opening = await getActiveOpening(contractAddress, ctx);
    if (opening === null) {
      toast("No active opening", "error");
      return;
    }
    if (!opening.isReadyToComplete) {
      toast(
        "Opening not yet ready, waiting for chainlink random number",
        "error"
      );
      return;
    }
    toast("Completing opening");
    await lootbox.methods
      .completeRandomLootboxOpening()
      .send({ from: ctx.account });
  };

  const openLootbox = async (lootboxId: number, count: number) => {
    console.log("openLootbox", lootboxId, count);
    // return useMutation(
    //     () => _openLootbox(lootboxId, count),
    //     {
    //         onSuccess: () => {
    //             toast("Lootbox opened", { type: "success" });
    //         }
    //     }
    // );
    _openLootbox(lootboxId, count);
  };

  const completeLootboxOpening = async () => {
    console.log("completeLootboxOpening");
    _completeLootboxOpening();
  };

  return {
    state,
    openLootbox,
    completeLootboxOpening,
  };
};

export default useLootboxToken;
