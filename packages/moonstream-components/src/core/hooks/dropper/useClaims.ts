import React from "react";
import { useQuery } from "react-query";
import { MoonstreamWeb3ProviderInterface } from "../../../../../../types/Moonstream";
import queryCacheProps from "../hookCommon";
import { queryHttp } from "../../utils/http";
const usePlayerClaims = ({
  ctx,
  playerAddress,
  contractAddress,
}: {
  ctx: MoonstreamWeb3ProviderInterface;
  initialPageSize: number;
  initialPage: number;
  playerAddress?: string;
  contractAddress?: string;
}) => {
  const [page, setPage] = React.useState(0);
  const [pageSize, setPageSize] = React.useState(0);

  const claimsList = useQuery(
    [
      "/play/drops",
      {
        dropper_contract_address: contractAddress,
        blockchain: ctx.targetChain?.name ?? "",
        claimant_address: playerAddress ?? ctx.account,
      },
    ],
    (query) => queryHttp(query).then((response: any) => response.data.drops),
    {
      ...queryCacheProps,
      enabled:
        !!contractAddress &&
        (!!playerAddress || !!ctx.account) &&
        !!ctx.targetChain?.name,
      onSuccess: () => {},
    }
  );

  const playerClaims = useQuery(
    [
      "/play/claims/batch",
      {
        blockchain: ctx.targetChain?.name ?? "",
        address: playerAddress ?? ctx.account,
        limit: pageSize,
        offset: page * pageSize,
      },
    ],
    (query: any) => queryHttp(query).then((response: any) => response.data),
    {
      ...queryCacheProps,
      keepPreviousData: true,
      onSuccess: () => {},
      enabled:
        pageSize !== 0 &&
        ctx.web3?.utils.isAddress(playerAddress ?? ctx.account),
    }
  );

  return { playerClaims, setPageSize, setPage, page, pageSize, claimsList };
};

export default usePlayerClaims;
