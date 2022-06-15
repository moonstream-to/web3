import { useQuery } from "react-query";
import { getTokenState } from "../contracts/erc20.contracts";
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";

const useERC20 = ({
  contractAddress,
  ctx,
}: {
  contractAddress: string;
  ctx: MoonstreamWeb3ProviderInterface;
}) => {
  const ERC20State = useQuery(
    ["ERC20State", ctx?.account, contractAddress, ctx.targetChain?.chainId],
    () => getTokenState({ ctx })(contractAddress),
    {
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) &&
        !!ctx.chainId &&
        ctx.chainId === ctx.targetChain?.chainId,
    }
  );

  return { ERC20State };
};

export default useERC20;
