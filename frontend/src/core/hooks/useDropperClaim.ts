import React, { useContext } from "react";
import Web3Context from "../providers/Web3Provider/context";
import BN from "bn.js";
import { getDropList, getDropMessage } from "../services/dropper.service";
import queryCacheProps from "./hookCommon";
import { useMutation, useQuery, UseQueryResult } from "react-query";
import { getState, claimDrop, getClaim } from "../contracts/dropper.contract";
import DataContext from "../providers/DataProvider/context";
import { ReactWeb3ProviderInterface } from "../../../types/Moonstream";
import { useToast } from "../../core/hooks";

const useDropperClaim = ({
  dropperAddress,
  targetChain,
  ctx,
  claimId,
}: {
  dropperAddress: string;
  targetChain: any;
  ctx: ReactWeb3ProviderInterface;
  claimId: string;
}) => {
  const toast = useToast();
  const claimStatus = useQuery(
    ["claimStatus", dropperAddress, targetChain.chainId, claimId],
    () => getClaim(dropperAddress, ctx)(claimId),
    {
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) && ctx.chainId === ctx.chainId,
    }
  );

  const claimWeb3Drop = useMutation(claimDrop(dropperAddress, ctx), {});

  const getClaimMessage = useMutation(getDropMessage(claimId), {
    onMutate: () => {},
    onSuccess: (response) => {
      claimWeb3Drop.mutate({
        message: response.data.signature,
        blockDeadline: response.data.block_deadline,
        claimId: claimId,
      });
      toast("Claim successful", "success");
    },
    onError: (error) => {},
    onSettled: () => {},
  });

  const claim = () => {
    getClaimMessage.mutate(ctx.account);
  };

  return { claimStatus, claim, claimWeb3Drop };
};

export default useDropperClaim;
