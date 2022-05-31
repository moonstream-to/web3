import { useQuery } from "react-query";

import {
  ChainInterface,
  MoonstreamWeb3ProviderInterface,
} from "../../../../../types/Moonstream";
import { getLootboxState } from "../contracts/lootbox.contract";

const useLootboxToken = ({
  contractAddress,
  targetChain,
  ctx,
}: {
  contractAddress: string;
  targetChain: ChainInterface;
  ctx: MoonstreamWeb3ProviderInterface;
}) => {
  const state = useQuery(
    ["LootboxState", contractAddress, targetChain.chainId],
    () => getLootboxState(contractAddress, ctx)(),
    {
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) &&
        ctx.chainId === targetChain.chainId,
    }
  );

  return {
    state,
  };
};

export default useLootboxToken;
