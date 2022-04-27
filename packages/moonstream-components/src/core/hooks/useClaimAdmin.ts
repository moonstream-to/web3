import React from "react";
import {
  getAdminList,
  getContracts,
  getTerminus,
  setClaimants,
} from "../services/moonstream-engine.service";
import { useMutation, useQuery } from "react-query";
import {
  ChainInterface,
  MoonstreamWeb3ProviderInterface,
} from "../../../../../types/Moonstream";
import { useToast } from ".";
import { balanceOfAddress } from "../contracts/terminus.contracts";

const useClaimAdmin = ({
  targetChain,
  ctx,
}: {
  targetChain: ChainInterface;
  ctx: MoonstreamWeb3ProviderInterface;
}) => {
  const toast = useToast();

  const contractsList = useQuery(
    ["contractsList"],
    () => getContracts()().then((data) => data.data),
    {
      onSuccess: () => {},
    }
  );

  const terminusList = useQuery(["terminusAddresses"], () =>
    getTerminus(targetChain.name)().then((response) => response.data)
  );

  const _hasAdminPermissions = React.useCallback(async () => {
    if (terminusList.data) {
      console.log("adminContracts terminusList.data", terminusList.data);
      const terminusAuthorizations = await Promise.all(
        terminusList.data.map(async (terminus: any) => {
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
        })
      );
      const terminusAdmin = terminusAuthorizations.filter(
        (item) => item[2] > 0
      );
      return terminusAdmin;
    }
  }, [terminusList.data, ctx]);

  const adminPermissions = useQuery(
    ["claimAdmin", "adminPermissions"],
    _hasAdminPermissions,
    {
      enabled: !!terminusList.data,
      onSuccess: () => {},
    }
  );

  const _getAdminClaimsList = async () => {
    const claimsByPermission = adminPermissions.data
      ? await Promise.all(
          adminPermissions.data.map(async (permission) => {
            console.log("permission map", permission);
            const response = await getAdminList(
              permission[0],
              targetChain.name,
              permission[1]
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
    ["claimAdmin", "adminClaims", targetChain.chainId],
    _getAdminClaimsList,
    {
      enabled: !!adminPermissions.data,
    }
  );

  const isLoading = React.useMemo(() => {
    if (terminusList.isLoading || contractsList.isLoading) return true;
    return false;
  }, [terminusList.isLoading, contractsList.isLoading]);

  const uploadFile = useMutation(setClaimants, {
    onSuccess: () => {
      toast("File uploaded successfully", "success");
    },
    onError: (error: any) => {
      toast("Uploading file failed", "error", "Error! >.<");
    },
    onSettled: () => {},
  });

  return {
    adminClaims,
    isLoading,
    uploadFile,
  };
};

export default useClaimAdmin;
