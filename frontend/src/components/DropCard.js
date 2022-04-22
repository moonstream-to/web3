import React, { useContext, useEffect, useState } from "react";
import {
  chakra,
  Flex,
  Text,
  Stack,
  Heading,
  Spinner,
  Button,
} from "@chakra-ui/react";
import useDropperClaim from "../core/hooks/useDropperClaim";
import Web3Context from "../core/providers/Web3Provider/context";
import { targetChain } from "../core/providers/Web3Provider";
import Erc20Card from "./Erc20Card";

const DropCard = ({ drop }) => {
  const web3Provider = useContext(Web3Context);

  const [ClaimData, setClaimData] = useState(false);
  const [ClaimAvailabel, setClaimAvailabel] = useState(false);

  const claimer = useDropperClaim({
    dropperAddress: process.env.NEXT_PUBLIC_DROPPER_ADDRESS ?? "",
    targetChain: targetChain,
    ctx: web3Provider,
    claimId: drop.id,
    ClaimAvailabel: ClaimAvailabel,
    ClaimData: ClaimData,
    dropperClaimId: drop.drop.id,
  });

  useEffect(() => {
    if (!claimer.claim.data) {
      claimer.claim.mutate();
    }
    if (claimer.claim.data && !ClaimAvailabel) {
      setClaimData(claimer.claim.data);
      setClaimAvailabel(true);
    }
  }, [claimer.claim.data]);

  console.log("drop", drop);

  console.log("claimer", claimer);
  console.log("claimer.claim.data", claimer.claim.data);
  console.log("claimer.state", claimer.state);
  console.log("ClaimAvailabel", ClaimAvailabel);
  console.log("ClaimData", ClaimData);

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
        {drop.drop.title}
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
        onClick={() =>
          claimer.claimWeb3Drop.mutate({
            message: ClaimData.data.signature,
            blockDeadline: ClaimData.data.block_deadline,
            claimId: ClaimData.data.claim_id,
            amount: ClaimData.data.amount,
          })
        }
        isLoading={claimer.data?.data}
        colorScheme={"orange"}
      >
        Claim
      </Button>
    </Flex>
  );
};

export default DropCard;
