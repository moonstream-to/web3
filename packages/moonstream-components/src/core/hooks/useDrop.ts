import React from "react";
import {
  deleteClaimants as _deleteClaimants,
  getClaimants,
  getClaim as _getClaim,
  activate,
  deactivate,
} from "../services/moonstream-engine.service";
import { useMutation, useQuery } from "react-query";
import {
  ChainInterface,
  MoonstreamWeb3ProviderInterface,
} from "../../../../../types/Moonstream";
import { useToast } from ".";
import queryCacheProps from "./hookCommon";
import useClaimAdmin from "./useDrops";

interface ClaimInterface {
  active: boolean;
  claim_block_deadline: number;
  claim_id: number;
  description: string;
  dropper_contract_address: string;
  id: string;
  terminus_address: string;
  terminus_pool_id: number;
  title: string;
}

const useClaim = ({
  targetChain,
  ctx,
  claimId,
  initialPageSize,
  getAll,
}: {
  targetChain: ChainInterface;
  ctx: MoonstreamWeb3ProviderInterface;
  claimId: string;
  initialPageSize?: number;
  getAll?: boolean;
}) => {
  console.log("useClaim");
  const admin = useClaimAdmin({ targetChain, ctx });
  const toast = useToast();

  const [claim, setClaim] = React.useState<ClaimInterface>(
    admin.adminClaims.data
  );
  React.useEffect(() => {
    if (admin.adminClaims.data || !admin.adminClaims.isLoading) {
      console.log("eff", admin.adminClaims.data);
      setClaim(
        admin.adminClaims.data?.find(
          (element: ClaimInterface) => element.id === claimId
        )
      );
    }
  }, [admin.adminClaims, claimId]);

  const [claimantsPage, setClaimantsPage] = React.useState(0);
  const [claimantsPageSize, setClaimantsPageSize] = React.useState(
    initialPageSize ?? 25
  );
  const _getClaimants = async (page: number) => {
    const response = await getClaimants({ dropperClaimId: claimId })({
      limit: claimantsPageSize,
      offset: page * claimantsPageSize,
    });
    console.log("_getClaimants", response);
    return response.data.drops;
  };
  const claimants = useQuery(
    ["claimants", "claimId", claimId, claimantsPage, claimantsPageSize],
    () => _getClaimants(claimantsPage),

    {
      ...queryCacheProps,
      keepPreviousData: true,
      onSuccess: () => {},
    }
  );

  // const getClaim = useQuery(
  //   ["getClaim", claimId, targetChain.chainId],
  //   _getClaim(targetChain.name)
  // );

  const deleteClaimants = useMutation(
    _deleteClaimants({ dropperClaimId: claimId }),
    {
      onSuccess: () => {
        toast("Revoked claim", "success");
        claimants.refetch();
      },
      onError: () => {
        toast("Revoking claim failed", "error", "Error! >.<");
      },
      onSettled: () => {},
    }
  );

  const activateDrop = useMutation(
    () => activate({ dropperClaimId: claimId }),
    {
      onSuccess: () => {
        toast("Activated drop", "success");
        admin.adminClaims.refetch();
      },
      onError: () => {
        toast("Activating drop failed", "error", "Error! >.<");
      },
      onSettled: () => {},
    }
  );

  const deactivateDrop = useMutation(
    () => deactivate({ dropperClaimId: claimId }),
    {
      onSuccess: () => {
        toast("Deactivated drop", "success");
        admin.adminClaims.refetch();
      },
      onError: () => {
        toast("Deactivating drop failed", "error", "Error! >.<");
      },
      onSettled: () => {},
    }
  );

  const _getAllclaimants = async () => {
    let _claimants = [];
    let offset = 0;
    let response = await getClaimants({ dropperClaimId: claimId })({
      limit: 500,
      offset: offset,
    });
    _claimants.push(...response.data.drops);

    while (response.data.drops.length == 500) {
      offset += 500;
      response = await getClaimants({ dropperClaimId: claimId })({
        limit: 500,
        offset: offset,
      });
      _claimants.push(...response.data.drops);
    }

    console.log("_getClaimants", _claimants);
    return _claimants;
  };

  const AllClaimants = useQuery(
    ["AllClaimants", "claimId", claimId],
    () => _getAllclaimants(),

    {
      ...queryCacheProps,
      keepPreviousData: true,
      onSuccess: () => {},
      enabled: getAll,
    }
  );

  return {
    claim,
    claimants,
    deleteClaimants,
    setClaimantsPage,
    claimantsPage,
    setClaimantsPageSize,
    claimantsPageSize,
    deactivateDrop,
    activateDrop,
    AllClaimants,
  };
};

export default useClaim;
