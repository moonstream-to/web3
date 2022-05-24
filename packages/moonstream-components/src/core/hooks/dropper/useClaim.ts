import React from "react";
import { getClaimSignature } from "../../services/moonstream-engine.service";
import { useMutation, useQuery } from "react-query";
import {
  claimDrop,
  getClaim,
  getSignerForClaim,
} from "../../contracts/dropper.contract";
import { MoonstreamWeb3ProviderInterface } from "../../../../../../types/Moonstream";
import { useToast } from "..";
import queryCacheProps from "../hookCommon";

const useClaim = ({
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

  console.log("useClaim", dropperAddress, claimId);
  const _getClaim = async (
    dropperAddress: string,
    ctx: MoonstreamWeb3ProviderInterface,
    claimId: string
  ) => {
    // let retval: ClaimerState = { canClaim: false, claim: [], status: "" };
    console.log("_getClaim", dropperAddress, ctx.account, claimId);
    let canClaim = false;
    const response = await getClaim(dropperAddress, ctx)(claimId);

    if (Number(response.status) > 0 || response.claim[0] == "0")
      canClaim = false;
    else canClaim = true;

    return { canClaim, ...response };
  };

  const state = useQuery(
    ["Claim", dropperAddress, targetChain.chainId, claimId],
    () => _getClaim(dropperAddress, ctx, claimId),
    {
      ...queryCacheProps,
      onSuccess: () => {},
      placeholderData: {
        canClaim: false,
        claim: ["", "", "", ""],
        status: "",
      },
      enabled: ctx.web3?.utils.isAddress(ctx.account) && !!ctx.chainId,
    }
  );

  const claimWeb3Drop = useMutation(claimDrop(dropperAddress, ctx), {
    onSuccess: () => {
      toast("Claim successful!", "success");
      state.refetch();
    },
    onError: (err) => {
      console.log("error", err);
    },
  });

  const signerForClaim = useQuery(
    ["signerForClaim", dropperAddress, targetChain.chainId, claimId],
    () => getSignerForClaim(dropperAddress, ctx)(claimId),
    {
      ...queryCacheProps,
      enabled: ctx.web3?.utils.isAddress(ctx.account) && !!ctx.chainId,
    }
  );

  const claim = useMutation(() => getClaimSignature(claimId, ctx.account), {
    onMutate: () => {},
    onSuccess: (response: any) => {
      console.log("response claim", response);
      claimWeb3Drop.mutate({
        message: response.data.signature,
        blockDeadline: response.data.block_deadline,
        amount: response.amount,
        claimId: claimId,
      });
    },
    onError: (error) => {
      console.log("error", error);
    },
    onSettled: () => {},
  });

  const isLoadingClaim = React.useMemo(() => {
    if (claimWeb3Drop.isLoading || claim.isLoading) return true;
    else return false;
  }, [claimWeb3Drop.isLoading, claim.isLoading]);

  return {
    state: state.data,
    claim,
    isLoadingClaim,
    isLoadingState: state.isLoading,
    claimWeb3Drop,
    signerForClaim,
  };
};

export default useClaim;
