import React, { useContext } from "react";
import Web3Context from "../providers/Web3Provider/context";
import BN from "bn.js";
import { getDropList, getDropMessage } from "../services/dropper.service";
import queryCacheProps from "./hookCommon";
import { useMutation, useQuery, UseQueryResult } from "react-query";
import { getState, claimDrop, getClaim } from "../contracts/dropper.contract";
import DataContext from "../providers/DataProvider/context";
import { ReactWeb3ProviderInterface } from "../../../types/Moonstream";

const useDropperClaim = ({
  dropperAddress,
  targetChain,
  ctx,
  claimId,
}: {
  dropperAddress: string;
  targetChain: any;
  ctx: ReactWeb3ProviderInterface;
  claimId: string;
}) => {
  const claimStatus = useQuery(
    ["claimStatus", dropperAddress, claimId, targetChain.chainId],
    async () => {
      console.log("TODO: implement this");
    },
    {
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) && ctx.chainId === ctx.chainId,
    }
  );

  const claimWeb3Drop = useMutation(claimDrop(dropperAddress, ctx), {});

  const getClaimMessage = useMutation(getDropMessage(claimId), {
    onMutate: () => {},
    onSuccess: (response) => {
      claimWeb3Drop.mutate({
        message: response.data.signature,
        blockDeadline: response.data.block_deadline,
        claimId: claimId,
      });
      //       block_deadline: 25946195
      // claim_id: 2
      // claimant: "0xCA618ea6Adb914B694E2acF1d77fe92894fbfA30"
      // signature: "f6869d03ccdb1482c57d2646ecd3f5b3fe2c8f5c52df2f4b9c6f34751d3a8ad478c3bf67f78ad006093f472b08bd0727f66294dab809766f521e7c5b274754b01b"
    },
    onError: (error) => {
      // toast(error, "error");
    },
    onSettled: () => {},
  });

  const claim = () => {
    getClaimMessage.mutate(ctx.account);
  };

  const getClaimState = useQuery(
    ["getClaimState", dropperAddress, targetChain.chainId, claimId],
    () => getClaim(dropperAddress, ctx)(claimId),
    {
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) && ctx.chainId === ctx.chainId,
    }
  );

  return { claimStatus, claim, claimWeb3Drop };
};

export default useDropperClaim;
