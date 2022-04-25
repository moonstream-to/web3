import React, { useContext } from "react";
import Web3Context from "../providers/Web3Provider/context";
import BN from "bn.js";
import { getDropList, getDropMessage } from "../services/moonstream-engine.service";
import queryCacheProps from "./hookCommon";
import { useMutation, useQuery, UseQueryResult } from "react-query";
import { getState, claimDrop, getClaim } from "../contracts/dropper.contract";
import DataContext from "../providers/DataProvider/context";
import { ReactWeb3ProviderInterface } from "../../../types/Moonstream";
import { getTokenState } from "../contracts/erc20.contracts";

const useERC20 = ({
  contractAddress,
  targetChain,
  ctx,
}: {
  contractAddress: string;
  targetChain: any;
  ctx: ReactWeb3ProviderInterface;
}) => {
  const ERC20State = useQuery(
    ["ERC20State", contractAddress, targetChain.chainId],
    () => getTokenState({ ctx })(contractAddress),
    {
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) &&
        ctx.chainId === targetChain.chainId,
    }
  );

  return { ERC20State };
};

export default useERC20;
