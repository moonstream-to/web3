import { useQuery } from "react-query";
import { getTokenState } from "../contracts/erc20.contracts";
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";

const useERC20 = ({
  contractAddress,
  targetChain,
  ctx,
}: {
  contractAddress: string;
  targetChain: any;
  ctx: MoonstreamWeb3ProviderInterface;
}) => {
  const ERC20State = useQuery(
    ["ERC20State", contractAddress, targetChain.chainId],
    () => getTokenState({ ctx })(contractAddress),
    {
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) &&
        ctx.chainId === targetChain.chainId,
    }
  );

  return { ERC20State };
};

export default useERC20;
