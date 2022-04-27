import React from "react";
import { useQuery } from "react-query";
import { getTerminusFacetPoolState } from "../contracts/terminus.contracts";
import useTerminus from "./useTerminus";
import * as abi from "../../../../../abi/MockTerminus.json";
import { MockTerminus as TerminusFacet } from "../../../../../types/contracts/MockTerminus";
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";

export interface useTerminusPoolArgumentsType {
  terminusAddress: string;
  poolId: string;
  targetChain: any;
  ctx: MoonstreamWeb3ProviderInterface;
}

const useTerminusPool = ({
  terminusAddress,
  poolId,
  targetChain,
  ctx,
}: useTerminusPoolArgumentsType) => {
  const terminus = useTerminus({
    diamondAddress: terminusAddress,
    targetChain: targetChain,
    ctx,
  });

  console.log("useTerminusPool", terminusAddress, poolId);
  const terminusPoolCache = useQuery(
    ["terminusPoolState", poolId, terminusAddress, targetChain.chainId],
    getTerminusFacetPoolState(ctx, terminusAddress, poolId),
    // getTerminusFacetState(ctx, terminusAddress),
    {
      onSuccess: () => {
        console.debug("succ");
      },
      refetchInterval: 1000000,
      staleTime: Infinity,
      enabled:
        !!terminus.terminusFacetCache.data?.paymentToken &&
        ctx.web3?.utils.isAddress(ctx.account) &&
        ctx.chainId === targetChain.chainId,
    }
  );

  const getMethodsABI = React.useCallback(
    <T extends keyof TerminusFacet["methods"]>(name: T): typeof abi[number] => {
      const index = abi.findIndex(
        (item) => item.name === name && item.type == "function"
      );
      if (index !== -1) {
        const item = abi[index];
        return item;
      } else throw "accesing wrong abi element";
    },
    []
  );

  return {
    terminusPoolCache,
    abi,
    getMethodsABI,
  };
};

export default useTerminusPool;
