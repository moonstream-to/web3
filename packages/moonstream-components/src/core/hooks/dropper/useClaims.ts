import React from "react";
import { useQuery } from "react-query";
import {
  ChainInterface,
  MoonstreamWeb3ProviderInterface,
} from "../../../../../../types/Moonstream";
import queryCacheProps from "../hookCommon";
import { queryHttp } from "../../utils/http";
const usePlayerClaims = ({
  targetChain,
  ctx,
  initialPageSize,
  initialPage,
  playerAddress,
  contractAddress,
}: {
  targetChain?: ChainInterface;
  ctx: MoonstreamWeb3ProviderInterface;
  initialPageSize: number;
  initialPage: number;
  playerAddress?: string;
  contractAddress?: string;
}) => {
  const [page, setPage] = React.useState(initialPage ?? 0);
  const [pageSize, setPageSize] = React.useState(initialPageSize ?? 10);

  const claimsList = useQuery(
    [
      "/drops/claims",
      {
        dropper_contract_address: contractAddress,
        blockchain: targetChain?.name ?? "",
        claimant_address: playerAddress ?? ctx.account,
      },
    ],
    (query) => queryHttp(query).then((response: any) => response.data.drops),
    {
      ...queryCacheProps,
      enabled: !!contractAddress && (!!playerAddress || !!ctx.account),
      onSuccess: () => {},
    }
  );

  const playerClaims = useQuery(
    [
      "/drops/batch",
      {
        blockchain: targetChain?.name ?? "",
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
        ctx.web3?.utils.isAddress(playerAddress ?? ctx.account) &&
        ctx.chainId === ctx.chainId,
    }
  );

  return { playerClaims, setPageSize, setPage, page, pageSize, claimsList };
};

export default usePlayerClaims;
