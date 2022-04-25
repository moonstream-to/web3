import React, { useContext } from "react";
import { Flex, Spinner } from "@chakra-ui/react";
import { TERMINUS_DIAMOND_ADDRESS } from "../AppDefintions";

import { targetChain } from "../core/providers/Web3Provider";

import useTerminus from "../core/hooks/useTerminus";
import PoolCard from "./PoolCard";
import TerminusControllerPanel from "./TerminusControllerPanel";
import Web3Context from "../core/providers/Web3Provider/context";
import TerminusOwnerPanel from "./TerminusOwnerPanel";

const Terminus = () => {
  const terminus = useTerminus({
    diamondAddress: TERMINUS_DIAMOND_ADDRESS,
    targetChain: targetChain,
  });

  const web3Provider = useContext(Web3Context);
  if (!terminus.terminusFacetCache.data?.totalPools) return <Spinner />;
  if (true) return <Spinner />;

  return (
    <Flex
      w="100%"
      minH="100vh"
      direction={"column"}
      maxW="1337px"
      alignSelf={"center"}
      px={["5px", "10px", "20px", "7%", null, "7%"]}
    >
      {terminus.terminusFacetCache.data.controller === web3Provider.account && (
        <TerminusControllerPanel
          borderRadius={"md"}
          my={2}
          bgColor="blue.600"
          py={4}
          direction={["column", "row"]}
        />
      )}
      {terminus.terminusFacetCache.data.owner === web3Provider.account && (
        <TerminusOwnerPanel
          borderRadius={"md"}
          my={2}
          bgColor="blue.600"
          py={4}
        />
      )}
      <Flex w="100%" direction="column">
        {terminus.terminusFacetCache.data.ownedPoolIds.map((i, idx) => (
          <PoolCard
            alignItems={"baseline"}
            // mx={["20px", "7%", null, "7%"]}
            maxW="1337px"
            key={`pool-${i}-${idx}`}
            poolId={String(i)}
            bgColor="blue.500"
          />
        ))}
      </Flex>
    </Flex>
  );
};

export default Terminus;
