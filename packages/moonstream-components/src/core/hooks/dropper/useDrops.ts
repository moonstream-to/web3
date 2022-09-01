import React from "react";
import {
  getAdminList,
  getTerminus,
} from "../../services/moonstream-engine.service";
import { useQuery } from "react-query";
import { MoonstreamWeb3ProviderInterface } from "../../../../../../types/Moonstream";
import { balanceOfAddress } from "../../contracts/terminus.contracts";
import queryCacheProps from "../hookCommon";
import { queryHttp } from "../../utils/http";

const useDrops = ({
  ctx,
  dropperAddress,
}: {
  dropperAddress?: string;
  ctx: MoonstreamWeb3ProviderInterface;
}) => {
  const [claimsPage, setClaimsPage] = React.useState(0);
  const [claimsPageSize, setClaimsPageSize] = React.useState(0);

  const terminusList = useQuery(
    ["terminusAddresses"],
    () =>
      getTerminus(ctx.targetChain?.name)().then((response) => response.data),
    {
      ...queryCacheProps,
      enabled:
        !!ctx.account &&
        !!ctx.chainId &&
        ctx.chainId === ctx.targetChain?.chainId,
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
              ctx.targetChain?.name,
              permission[1],
              claimsPage * claimsPageSize,
              claimsPageSize,
              dropperAddress
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
    [
      "claimAdmin",
      "adminClaims",
      ctx.targetChain?.name,
      claimsPage,
      claimsPageSize,
      dropperAddress,
    ],
    _getAdminClaimsList,
    {
      ...queryCacheProps,
      keepPreviousData: true,
      enabled:
        !!adminPermissions.data &&
        !!ctx.account &&
        !!ctx.targetChain?.name &&
        claimsPageSize != 0,
    }
  );

  const pageOptions = {
    page: claimsPage,
    setPage: setClaimsPage,
    pageSize: claimsPageSize,
    setPageSize: setClaimsPageSize,
  };

  const dropperContracts = useQuery(
    ["/play/drops/contracts", { blockchain: ctx.targetChain?.name }],
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
    pageOptions,
    dropperContracts,
  };
};

export default useDrops;
