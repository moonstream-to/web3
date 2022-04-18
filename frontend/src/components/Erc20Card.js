import React, { useContext } from "react";
import {
  chakra,
  Flex,
  Text,
  Stack,
  Heading,
  Spinner,
  Button,
  Badge,
} from "@chakra-ui/react";
import useDropperClaim from "../core/hooks/useDropperClaim";
import Web3Context from "../core/providers/Web3Provider/context";
import { targetChain } from "../core/providers/Web3Provider";
import useErc20 from "../core/hooks/useERC20";
const ERC20Card = ({ address, amount, isLoading }) => {
  const web3Provider = useContext(Web3Context);

  const erc20 = useErc20({
    contractAddress: address,
    ctx: web3Provider,
    targetChain: targetChain,
  });
  if (erc20.ERC20State.isLoading || isLoading) return <Spinner size="sm" />;
  if (!erc20.ERC20State.data) return "whops";
  console.log("erc20", erc20.ERC20State.data);
  return (
    <Badge size="md" colorScheme={"blue"}>
      {erc20.ERC20State.data.symbol} : {amount}
    </Badge>
  );
};

export default ERC20Card;
