import React, { useContext } from "react";
import { Spinner, Badge } from "@chakra-ui/react";
import Web3Context from "../core/providers/Web3Provider/context";
import useErc20 from "../core/hooks/useERC20";
const ERC20Card = ({ address, amount, isLoading }) => {
  const web3Provider = useContext(Web3Context);

  const erc20 = useErc20({
    contractAddress: address,
    ctx: web3Provider,
  });
  if (erc20.ERC20State.isLoading || isLoading) return <Spinner size="sm" />;
  if (!erc20.ERC20State.data) return "whops";
  return (
    <Badge size="md" colorScheme={"blue"}>
      {erc20.ERC20State.data.symbol} : {amount}
    </Badge>
  );
};

export default ERC20Card;
