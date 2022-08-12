import { useQuery } from "react-query";

import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";
import { getLootboxState } from "../contracts/lootbox.contract";

const useLootboxToken = ({
  contractAddress,
  ctx,
}: {
  contractAddress: string;
  ctx: MoonstreamWeb3ProviderInterface;
}) => {
  const state = useQuery(
    ["LootboxState", contractAddress, ctx.targetChain?.chainId],
    () => getLootboxState(contractAddress, ctx)(),
    {
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) &&
        !!ctx.chainId &&
        ctx.chainId === ctx.targetChain?.chainId,
    }
  );

  return {
    state,
  };
};

export default useLootboxToken;
