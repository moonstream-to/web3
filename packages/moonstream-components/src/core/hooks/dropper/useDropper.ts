import queryCacheProps from "../hookCommon";
import { useQuery } from "react-query";
import { getState } from "../../contracts/dropper.contract";
import { MoonstreamWeb3ProviderInterface } from "../../../../../../types/Moonstream";
import { queryHttp } from "../../utils/http";
const useDropper = ({
  dropperAddress,
  targetChain,
  ctx,
}: {
  dropperAddress: string;
  targetChain: any;
  ctx: MoonstreamWeb3ProviderInterface;
}) => {
  const dropperWeb3State = useQuery(
    ["dropperContractState", dropperAddress, targetChain.chainId],
    () => getState(dropperAddress, ctx)(),
    {
      ...queryCacheProps,
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) && ctx.chainId === ctx.chainId,
    }
  );

  const dropperContracts = useQuery(
    ["/drops/contracts", { blockchain: targetChain.name }],
    (query: any) => queryHttp(query).then((result: any) => result.data),
    {
      ...queryCacheProps,
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) && ctx.chainId === ctx.chainId,
    }
  );

  return { dropperWeb3State, dropperContracts };
};

export default useDropper;
