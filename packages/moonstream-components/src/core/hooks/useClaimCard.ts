import React from "react";
import {
  getAdminList,
  getClaimants,
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
import queryCacheProps from "./hookCommon";

const useClaimCard = ({
  targetChain,
  ctx,
  claimId,
}: {
  targetChain: ChainInterface;
  ctx: MoonstreamWeb3ProviderInterface;
  claimId: string;
}) => {
  const adminPermissions = useQuery(
    ["claimants", "claimId", claimId],
    () =>
      getClaimants({ dropperClaimId: claimId })({ limit: 9999999, offset: 0 }),
    {
      ...queryCacheProps,
      onSuccess: () => {},
    }
  );

  return adminPermissions;
};

export default useClaimCard;
