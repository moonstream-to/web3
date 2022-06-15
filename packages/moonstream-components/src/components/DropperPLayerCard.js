import React, { useContext } from "react";
import { Flex, Text, Button } from "@chakra-ui/react";
import useDropperClaim from "../core/hooks/useDropperClaim";
import Web3Context from "../core/providers/Web3Provider/context";
import Erc20Card from "./Erc20Card";

const DropCard = ({ drop }) => {
  const web3Provider = useContext(Web3Context);

  const claimer = useDropperClaim({
    dropperAddress: "",
    ctx: web3Provider,
    claimId: drop.id,
  });

  return (
    <Flex
      bgColor="blue.600"
      borderRadius="md"
      px={4}
      py={2}
      flexGrow={1}
      alignContent="baseline"
      justifyContent={"space-between"}
      alignItems="baseline"
    >
      <Text fontWeight={600} textColor="gray.100" h="min-content">
        {drop.entry.title}
      </Text>
      {claimer.state && claimer.state.claim[0] == "20" && (
        <Erc20Card
          isLoading={claimer.isLoadingState}
          address={claimer.state.claim[1]}
          amount={web3Provider.web3.utils.fromWei(
            claimer.state.claim[3],
            "ether"
          )}
        />
      )}
      <Button
        isDisabled={!claimer.state.canClaim}
        onClick={() => claimer.claim.mutate()}
        isLoading={claimer.isLoadingClaim}
        colorScheme={"orange"}
      >
        Claim
      </Button>
    </Flex>
  );
};

export default DropCard;
