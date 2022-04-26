import React, { useContext } from "react";
import Web3Context from "../providers/Web3Provider/context";
import BN from "bn.js";
import {
  getDropList,
  getDropMessage,
} from "../services/moonstream-engine.service";
import queryCacheProps from "./hookCommon";
import { useMutation, useQuery, UseQueryResult } from "react-query";
import { getState, claimDrop, getClaim } from "../contracts/dropper.contract";
import DataContext from "../providers/DataProvider/context";
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";
import { useToast } from "../../core/hooks";

interface ClaimerState {
  canClaim: boolean;
  claim: Array<String>;
  status: string;
}

const useDrop = ({
  dropperAddress,
  targetChain,
  ctx,
  claimId,
}: {
  dropperAddress: string;
  targetChain: any;
  ctx: MoonstreamWeb3ProviderInterface;
  claimId: string;
}) => {
  const toast = useToast();

  const _getClaim = async (
    dropperAddress: string,
    ctx: MoonstreamWeb3ProviderInterface,
    claimId: string
  ) => {
    // let retval: ClaimerState = { canClaim: false, claim: [], status: "" };
    let canClaim = false;
    const response = await getClaim(dropperAddress, ctx)(claimId);

    if (Number(response.status) > 0 || response.claim[0] == "0")
      canClaim = false;
    else canClaim = true;

    return { canClaim, ...response };
  };

  const state = useQuery(
    ["useDrop", dropperAddress, targetChain.chainId, claimId],
    () => _getClaim(dropperAddress, ctx, claimId),
    {
      onSuccess: () => {},
      initialData: {
        canClaim: false,
        claim: ["", "", "", ""],
        status: "",
      },
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) &&
        ctx.chainId === ctx.chainId &&
        claimId !== "0",
    }
  );

  return state;
};

export default useDrop;
