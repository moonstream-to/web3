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

interface ClaimerState {
  canClaim: boolean;
  claim: Array<String>;
  status: string;
}

const useDropperClaim = ({
  dropperAddress,
  targetChain,
  ctx,
  dropperClaimId,
  ClaimAvailabel,
  ClaimData,
}: {
  dropperAddress: string;
  targetChain: any;
  ClaimAvailabel: any;
  ClaimData: any;
  ctx: ReactWeb3ProviderInterface;
  claimId: string;
  dropperClaimId: string;
}) => {
  const toast = useToast();

  let claimId = "";

  const claim = useMutation(() => getDropMessage(dropperClaimId)(ctx.account), {
    onMutate: () => {},
    onSuccess: (response) => {
      // claimWeb3Drop.mutate({
      //   message: response.data.signature,
      //   blockDeadline: response.data.block_deadline,
      //   claimId: response.data.claimId,
      //   amount: response.data.amount,
      // });
    },
    onError: (error) => {},
    onSettled: () => {},
  });

  const _getClaim = async (
    dropperAddress: string,
    ctx: ReactWeb3ProviderInterface,
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
    [
      "LootboxClaimState",
      dropperAddress,
      targetChain.chainId,
      ClaimData?.data?.claim_id,
    ],
    () => _getClaim(dropperAddress, ctx, ClaimData?.data?.claim_id),
    {
      onSuccess: () => {},
      initialData: {
        canClaim: false,
        claim: ["", "", "", ""],
        status: "",
      },
      enabled:
        ClaimAvailabel &&
        ctx.web3?.utils.isAddress(ctx.account) &&
        ctx.chainId === ctx.chainId,
    }
  );

  const claimWeb3Drop = useMutation(claimDrop(dropperAddress, ctx), {
    onSuccess: (resonse) => {
      toast("Claim successful", "success");
      state.refetch();
    },
  });

  const isLoadingClaim = React.useMemo(() => {
    if (claimWeb3Drop.isLoading || claim.isLoading) return true;
    else return false;
  }, [claimWeb3Drop.isLoading, claim.isLoading]);

  return {
    state: state.data,
    claim,
    claimWeb3Drop,
    isLoadingClaim,
    isLoadingState: state.isLoading,
  };
};

export default useDropperClaim;
