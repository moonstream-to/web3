import React, { useContext, useEffect } from "react";
import Web3Context from "../providers/Web3Provider/context";
import BN from "bn.js";
import {
  getAdminList,
  getContracts,
  getDropList,
  getDropMessage,
  getTerminus,
  setClaimants,
} from "../services/moonstream-engine.service";
import queryCacheProps from "./hookCommon";
import { useMutation, useQuery, UseQueryResult } from "react-query";
import { getState, claimDrop, getClaim } from "../contracts/dropper.contract";
import DataContext from "../providers/DataProvider/context";
import {
  ChainInterface,
  MoonstreamWeb3ProviderInterface,
} from "../../../../../types/Moonstream";
import { useToast } from ".";
import { balanceOfAddress } from "../contracts/terminus.contracts";

interface ClaimerState {
  canClaim: boolean;
  claim: Array<String>;
  status: string;
}

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

  const _getDropList = async () => {
    const claimsByPermission = adminPermissions.data
      ? await Promise.all(
          contractsList.data.map(async (contractInList: any) => {
            const response = await getDropList(
              contractInList.address,
              contractInList.blockchain,
              ctx
            )();
            return {
              address: contractInList.address,
              blockchain: contractInList.blockchain,
              claims: response.data.drops,
            };
          })
        )
      : [];
    const claims: any = [];
    claimsByPermission.forEach((_item) => claims.push(..._item));
    console.log("claimsByPermission", claimsByPermission, claims);
    return claims;
  };

  // const allDrops = useQuery(["allDrops"], _getDropList, {
  //   enabled: !!contractsList.data,
  //   onSuccess: () => {},
  // });

  // console.log("allDrops", allDrops.data);

  const terminusList = useQuery(["terminusAddresses"], () =>
    getTerminus(targetChain.name)().then((response) => response.data)
  );

  const _hasAdminPermissions = React.useCallback(async () => {
    if (terminusList.data) {
      console.log("adminContracts terminusList.data", terminusList.data);
      console.log("adminContracts contractsList.data", contractsList.data);
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
  }, [terminusList.data]);

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
      toast("Created new dashboard", "success");
    },
    onError: (error: any) => {
      toast(error.error, "error", "Fail");
    },
    onSettled: () => {},
  });

  return {
    adminClaims,
    isLoading,
    uploadFile,
    // contractsList,
    // terminusList,
  };
};

export default useClaimAdmin;
