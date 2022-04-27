import React from "react";
import { getDropMessage } from "../services/moonstream-engine.service";
import { useMutation, useQuery } from "react-query";
import { claimDrop, getClaim } from "../contracts/dropper.contract";
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";
import { useToast } from "../../core/hooks";

const useDropperClaim = ({
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
    ["LootboxClaimState", dropperAddress, targetChain.chainId, claimId],
    () => _getClaim(dropperAddress, ctx, claimId),
    {
      onSuccess: () => {},
      initialData: {
        canClaim: false,
        claim: ["", "", "", ""],
        status: "",
      },
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) && ctx.chainId === ctx.chainId,
    }
  );

  const claimWeb3Drop = useMutation(claimDrop(dropperAddress, ctx), {
    onSuccess: () => {
      toast("Claim successful", "success");
      state.refetch();
    },
  });

  const claim = useMutation(() => getDropMessage(claimId)(ctx.account), {
    onMutate: () => {},
    onSuccess: (response) => {
      claimWeb3Drop.mutate({
        message: response.data.signature,
        blockDeadline: response.data.block_deadline,
        claimId: claimId,
      });
    },
    onError: () => {},
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
  };
};

export default useDropperClaim;
