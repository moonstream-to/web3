import React from "react";
import {
  deleteClaimants as _deleteClaimants,
  getClaimants,
  activate,
  deactivate,
  setClaimants,
} from "../../services/moonstream-engine.service";
import { useMutation, useQuery, useQueryClient } from "react-query";
import {
  MoonstreamWeb3ProviderInterface,
  UpdateClaim,
} from "../../../../../../types/Moonstream";
import useToast from "../useToast";
import queryCacheProps from "../hookCommon";
import useDrops from "./useDrops";
import { patchHttp } from "../../utils/http";

const useDrop = ({
  ctx,
  claimId,
  getAll,
}: {
  ctx: MoonstreamWeb3ProviderInterface;
  claimId?: string;
  initialPageSize?: number;
  getAll?: boolean;
}) => {
  const admin = useDrops({ ctx });
  const toast = useToast();
  const queryClient = useQueryClient();

  const [claimantsPage, setClaimantsPage] = React.useState(0);
  const [claimantsPageSize, setClaimantsPageSize] = React.useState(0);
  const _getClaimants = async (page: number) => {
    const response = await getClaimants({ dropperClaimId: claimId })({
      limit: claimantsPageSize,
      offset: page * claimantsPageSize,
    });
    return response.data.claimants;
  };
  const claimants = useQuery(
    ["claimants", "claimId", claimId, claimantsPage, claimantsPageSize],
    () => _getClaimants(claimantsPage),

    {
      ...queryCacheProps,
      enabled: !!ctx.account && claimantsPageSize != 0,
      onSuccess: () => {},
    }
  );

  const deleteClaimants = useMutation(
    _deleteClaimants({ dropperClaimId: claimId }),
    {
      onSuccess: () => {
        toast("Revoked claim", "success");
        claimants.refetch();
        queryClient.refetchQueries("/drops/claimants/search");
        queryClient.refetchQueries(["claimants", "claimId", claimId]);
      },
      onError: () => {
        toast("Revoking claim failed", "error", "Error! >.<");
      },
      onSettled: () => {},
    }
  );

  const activateDrop = useMutation(activate, {
    onSuccess: () => {
      toast("Activated drop", "success");
      admin.adminClaims.refetch();
    },
    onError: () => {
      toast("Activating drop failed", "error", "Error! >.<");
    },
    onSettled: () => {},
  });

  const deactivateDrop = useMutation(deactivate, {
    onSuccess: () => {
      toast("Deactivated drop", "success");
      admin.adminClaims.refetch();
    },
    onError: () => {
      toast("Deactivating drop failed", "error", "Error! >.<");
    },
    onSettled: () => {
      deactivateDrop.reset();
    },
  });

  const _getAllclaimants = async () => {
    let _claimants = [];
    let offset = 0;
    let response = await getClaimants({ dropperClaimId: claimId })({
      limit: 500,
      offset: offset,
    });
    _claimants.push(...response.data.claimants);

    while (response.data.drops.length == 500) {
      offset += 500;
      response = await getClaimants({ dropperClaimId: claimId })({
        limit: 500,
        offset: offset,
      });
      _claimants.push(...response.data.claimants);
    }

    return _claimants;
  };

  const AllClaimants = useQuery(
    ["AllClaimants", "claimId", claimId],
    () => _getAllclaimants(),

    {
      ...queryCacheProps,
      keepPreviousData: true,
      onSuccess: () => {},
      enabled: !!getAll,
    }
  );

  const update = useMutation(
    (data: UpdateClaim) => {
      if (claimId) return patchHttp(`/admin/drops/${claimId}`, { ...data });
      else throw new Error("Cannot use update without claimid");
    },
    {
      onSuccess: () => {
        admin.adminClaims.refetch();
        toast("Updated drop info", "success");
      },
      onError: () => {
        toast("Updating drop failed >.<", "error");
      },
    }
  );

  const uploadFile = useMutation(setClaimants, {
    onSuccess: () => {
      toast("File uploaded successfully", "success");
    },
    onError: () => {
      toast("Uploading file failed", "error", "Error! >.<");
    },
    onSettled: () => {},
  });

  return {
    claimants,
    deleteClaimants,
    setClaimantsPage,
    claimantsPage,
    setClaimantsPageSize,
    claimantsPageSize,
    deactivateDrop,
    activateDrop,
    AllClaimants,
    update,
    uploadFile,
  };
};

export default useDrop;
