import React from "react";
import {
  activate,
  deactivate,
  getAdminList,
  getTerminus,
  setClaimants,
  updateDrop,
} from "../../services/moonstream-engine.service";
import { useMutation, useQuery } from "react-query";
import {
  ChainInterface,
  MoonstreamWeb3ProviderInterface,
  updateDropArguments,
} from "../../../../../../types/Moonstream";
import useToast from "../useToast";
import { balanceOfAddress } from "../../contracts/terminus.contracts";
import queryCacheProps from "../hookCommon";
import { queryHttp } from "../../utils/http";

const useDrops = ({
  targetChain,
  ctx,
}: {
  targetChain: ChainInterface;
  ctx: MoonstreamWeb3ProviderInterface;
}) => {
  const toast = useToast();

  const [claimsPage, setClaimsPage] = React.useState(0);
  const [claimsPageSize, setClaimsPageSize] = React.useState(0);

  const terminusList = useQuery(
    ["terminusAddresses"],
    () => getTerminus(targetChain.name)().then((response) => response.data),
    {
      ...queryCacheProps,
      enabled: !!ctx.account,
    }
  );

  const _hasAdminPermissions = React.useCallback(async () => {
    if (terminusList.data) {
      const terminusAuthorizations = await Promise.all(
        terminusList.data.map(
          async (terminus: {
            terminus_address: string;
            terminus_pool_id: number;
          }) => {
            return [
              terminus.terminus_address,
              terminus.terminus_pool_id,
              await balanceOfAddress(
                ctx.account,
                terminus.terminus_address,
                terminus.terminus_pool_id,
                ctx
              )(),
            ];
          }
        )
      );
      //terminusAuthorizations = [[terminus_addess, poolId, balance]]
      const terminusAdmin = terminusAuthorizations.filter(
        (item: any) => item[2] > 0
      );
      return terminusAdmin;
    }
  }, [terminusList.data, ctx]);

  const adminPermissions = useQuery(
    ["claimAdmin", "adminPermissions", ctx.account],
    _hasAdminPermissions,
    {
      ...queryCacheProps,
      enabled: !!terminusList.data && !!ctx.account,
      onSuccess: () => {},
      onError: (err) => {
        console.error("adminPermissions err", err);
      },
    }
  );

  const _getAdminClaimsList = async () => {
    const claimsByPermission = adminPermissions.data
      ? await Promise.all(
          adminPermissions.data.map(async (permission: any) => {
            const response = await getAdminList(
              permission[0],
              targetChain.name,
              permission[1],
              claimsPage * claimsPageSize,
              claimsPageSize
            )();
            return response.data.drops;
          })
        )
      : [];
    const claims: any = [];
    claimsByPermission.forEach((_item) => claims.push(..._item));
    return claims;
  };

  const adminClaims = useQuery(
    ["claimAdmin", "adminClaims", targetChain.name, claimsPage, claimsPageSize],
    _getAdminClaimsList,
    {
      ...queryCacheProps,
      keepPreviousData: true,
      enabled:
        !!adminPermissions.data &&
        !!ctx.account &&
        !!targetChain.name &&
        claimsPageSize != 0,
    }
  );

  const isLoading = React.useMemo(() => {
    if (terminusList.isLoading) return true;
    return false;
  }, [terminusList.isLoading]);

  const uploadFile = useMutation(setClaimants, {
    onSuccess: () => {
      toast("File uploaded successfully", "success");
    },
    onError: () => {
      toast("Uploading file failed", "error", "Error! >.<");
    },
    onSettled: () => {},
  });

  const pageOptions = {
    page: claimsPage,
    setPage: setClaimsPage,
    pageSize: claimsPageSize,
    setPageSize: setClaimsPageSize,
  };

  const update = useMutation(
    ({ id, data }: { id: string; data: updateDropArguments }) =>
      updateDrop({ dropperClaimId: id })({ ...data }),
    {
      onSuccess: () => {
        adminClaims.refetch();
        toast("Updated drop info", "success");
      },
      onError: () => {
        toast("Updating drop failed >.<", "error");
      },
    }
  );

  const activateDrop = useMutation(
    (id: string) => activate({ dropperClaimId: id }),
    {
      onSuccess: () => {
        toast("Activated drop", "success");
        adminClaims.refetch();
      },
      onError: () => {
        toast("Activating drop failed", "error", "Error! >.<");
      },
      onSettled: () => {},
    }
  );

  const deactivateDrop = useMutation(
    (id: string) => deactivate({ dropperClaimId: id }),
    {
      onSuccess: () => {
        toast("Deactivated drop", "success");
        adminClaims.refetch();
      },
      onError: () => {
        toast("Deactivating drop failed", "error", "Error! >.<");
      },
      onSettled: () => {
        deactivateDrop.reset();
      },
    }
  );

  const dropperContracts = useQuery(
    ["/drops/contracts", { blockchain: targetChain.name }],
    (query: any) => queryHttp(query).then((result: any) => result.data),
    {
      ...queryCacheProps,
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) && ctx.chainId === ctx.chainId,
    }
  );

  return {
    adminClaims,
    isLoading,
    uploadFile,
    pageOptions,
    update,
    activateDrop,
    deactivateDrop,
    dropperContracts,
  };
};

export default useDrops;
