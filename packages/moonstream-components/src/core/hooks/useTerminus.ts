import React, { useContext } from "react";
import BN from "bn.js";
import { useMutation, useQuery, UseQueryResult } from "react-query";
import { getTerminusFacetState } from "../contracts/terminus.contracts";
import { getTokenState } from "../contracts/erc20.contracts";
import { getTerminus } from "../services/terminus.service";
import queryCacheProps from "./hookCommon";
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";

export interface TerminusHookArguments {
  diamondAddress: string;
  targetChain: any;
  ctx: MoonstreamWeb3ProviderInterface;
}
// const diamondJSON = require("../../../../build/contracts/Diamond.json");
const terminusFacetJSON = require("../../../../../abi/MockTerminus.json");
// const moonstreamTokenFaucetJSON = require("../../../../build/contracts/MoonstreamTokenFaucet.json");
const useTerminus = ({
  diamondAddress,
  targetChain,
  ctx,
}: TerminusHookArguments) => {
  //   React.useEffect(() => {
  //     if (!contracts["terminusFacet"]) {
  //       dispatchContracts({
  //         key: "terminusFacet",
  //         abi: terminusFacetJSON, //Facet abi
  //         address: diamondAddress, // Diamond address
  //       });
  //     }
  //     if (!contracts["ownershipFacet"]) {
  //       dispatchContracts({
  //         key: "ownershipFacet",
  //         address: diamondAddress, // Diamond address
  //       });
  //     }
  //   }, [contracts, diamondAddress, targetChain, dispatchContracts]);

  const terminusFacetCache = useQuery(
    ["terminusFacet", diamondAddress, targetChain.chainId],
    getTerminusFacetState(ctx, diamondAddress),
    {
      onSuccess: () => {},
      enabled:
        // !!contracts["ownershipFacet"] &&
        // !!contracts["terminusFacet"] &&
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
