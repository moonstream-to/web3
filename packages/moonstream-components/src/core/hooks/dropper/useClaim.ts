import React from "react";
import { getClaimSignature } from "../../services/moonstream-engine.service";
import { useMutation, useQuery } from "react-query";
import { MoonstreamWeb3ProviderInterface } from "../../../../../../types/Moonstream";
import { useToast } from "..";
import queryCacheProps from "../hookCommon";
import useDropperContract from "./useDropper.sol";
import { queryHttp } from "../../utils/http";

const useClaim = ({
  dropperAddress,
  ctx,
  claimId,
  claimantAddress,
  userAccess,
}: {
  claimantAddress?: string;
  dropperAddress?: string;
  ctx: MoonstreamWeb3ProviderInterface;
  claimId: string;
  userAccess?: boolean;
}) => {
  const toast = useToast();

  const claim = useQuery(
    [`/play/drops/${claimId}`],
    (query: any) => queryHttp(query).then((r: any) => r.data),
    {
      ...queryCacheProps,
      enabled: !!claimId && !userAccess,
    }
  );

  const { claimWeb3Drop } = useDropperContract({
    dropperAddress,
    ctx,
    claimId: claim.data?.claim_id,
  });

  const claimSeq = useMutation(
    () => getClaimSignature({ claimId, address: ctx.account }),
    {
      onMutate: () => {},
      onSuccess: (data: any) => {
        claimWeb3Drop.mutate({
          message: data.signature,
          blockDeadline: data.block_deadline,
          amount: data.amount,
          claimId: data.claim_id,
        });
      },
      onError: () => {
        toast("Failed to get claim signature from API >.<", "error");
      },
      onSettled: () => {},
    }
  );

  const signature = useQuery(
    [`/play/claims/${claimId}`, { address: claimantAddress }],
    (query: any) => queryHttp(query).then((r: any) => r.data),
    {
      ...queryCacheProps,
      // cacheTime: 0,
      enabled: !!claimId && ctx.web3.utils.isAddress(claimantAddress ?? ""),
    }
  );

  const isLoadingClaim = React.useMemo(() => {
    if (claimWeb3Drop.isLoading || claim.isLoading) return true;
    else return false;
  }, [claimWeb3Drop.isLoading, claim.isLoading]);

  return {
    claim,
    isLoadingClaim,
    claimSeq,
    signature,
  };
};

export default useClaim;
