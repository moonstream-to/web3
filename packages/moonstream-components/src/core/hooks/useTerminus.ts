import { useQuery } from "react-query";
import { getTerminusFacetState } from "../contracts/terminus.contracts";
import { getTokenState } from "../contracts/erc20.contracts";
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";

export interface TerminusHookArguments {
  diamondAddress: string;
  targetChain: any;
  ctx: MoonstreamWeb3ProviderInterface;
}
const useTerminus = ({
  diamondAddress,
  targetChain,
  ctx,
}: TerminusHookArguments) => {
  const terminusFacetCache = useQuery(
    ["terminusFacet", diamondAddress, targetChain.chainId],
    getTerminusFacetState(ctx, diamondAddress),
    {
      onSuccess: () => {},
      enabled:
        ctx?.web3?.utils.isAddress(ctx.account) &&
        ctx.chainId === targetChain.chainId,
    }
  );

  const terminusPaymentTokenCache = useQuery(
    ["terminus", "terminusPaymentToken", terminusFacetCache.data?.paymentToken],
    (query) =>
      getTokenState({
        ctx,
        spender: diamondAddress,
        account: ctx.account,
      })(query.queryKey[2] ?? ""),
    {
      onSuccess: () => {},
      enabled:
        !!terminusFacetCache.data?.paymentToken &&
        ctx?.web3?.utils.isAddress(ctx.account) &&
        ctx.chainId === targetChain.chainId,
    }
  );

  return {
    terminusFacetCache,
    terminusPaymentTokenCache,
  };
};

export default useTerminus;
