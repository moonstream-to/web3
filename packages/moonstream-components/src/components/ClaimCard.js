import React, { useContext } from "react";
import {
  chakra,
  Flex,
  Heading,
  Spinner,
  UnorderedList,
  ListItem,
  Button,
} from "@chakra-ui/react";
import useClaim from "../core/hooks/dropper/useClaim";
import Web3Context from "../core/providers/Web3Provider/context";
import { targetChain } from "../core/providers/Web3Provider";

const _ClaimCard = ({ drop, children, ...props }) => {
  const web3Provider = useContext(Web3Context);

  const claimer = useClaim({
    dropperAddress: drop.dropper_contract_address,
    targetChain: targetChain,
    ctx: web3Provider,
    claimId: drop.claim_id,
  });

  if (
    claimer.claimStatus?.data &&
    (claimer.claimStatus?.data.status > 0 ||
      claimer.claimStatus?.data.claim[0] == "0")
  )
    if (claimer.isLoadingClaim) return <Spinner />;

  console.log("claimCard", drop);
  console.log("type is", claimer.state.claim.tokenType);

  return (
    <Flex
      borderRadius={"md"}
      bgColor="blue.800"
      w="100%"
      direction={"column"}
      p={4}
      mt={2}
      textColor={"gray.300"}
      {...props}
    >
      <Heading as={"h2"} fontSize="lg" w="90%" mt={2}>
        {drop.title}
      </Heading>
      <Heading as={"h3"} fontSize="md">
        {drop.description}
      </Heading>
      <Flex w="100%" direction={["row", null]} flexWrap="wrap">
        <Flex
          direction={"row"}
          flexGrow={1}
          flexBasis={"200px"}
          wordBreak="break-word"
        >
          <Flex
            m={2}
            direction={"row"}
            minW="200px"
            flexWrap={"wrap"}
            w="100%"
            bgColor={"blue.1100"}
            borderRadius="md"
            px={2}
            // pt={4}
          >
            <UnorderedList fontSize={"sm"}>
              <ListItem>
                Deadline: &#9;&#9;&#9;&#9;&#9;&#9;&#9;
                {drop.block_deadline}
              </ListItem>
              <ListItem>
                Dropper: <code>{drop.dropper_contract_address}</code>
              </ListItem>
              <ListItem>
                Amount: <code>{drop.amount}</code>
              </ListItem>
              <ListItem>tokenType: {claimer.state.claim.tokenType}</ListItem>
              <ListItem>claimd id: {drop.claim_id}</ListItem>
            </UnorderedList>
          </Flex>
        </Flex>
        <Flex
          //TODO: add claim metadata here
          flexGrow={1}
          m={2}
          h="auto"
          flexBasis={"220px"}
          bgColor={"red.500"}
          borderRadius="md"
        ></Flex>
      </Flex>
      <Flex direction={"row"} justifyContent="space-evenly" pt={4}>
        <Button
          variant={"solid"}
          size="xl"
          isLoading={claimer.claimWeb3Drop.isLoading}
          colorScheme="green"
          isDisabled={!claimer.state.canClaim}
          onClick={() =>
            claimer.claimWeb3Drop.mutate({
              message: drop.signature,
              blockDeadline: drop.block_deadline,
              claimId: drop.claim_id,
              amount: drop.amount_string,
            })
          }
        >
          {claimer.state.canClaim ? "Claim now" : "Already claimed"}
        </Button>
      </Flex>
      {children && children}
    </Flex>
  );
};
const ClaimCard = chakra(_ClaimCard);
export default ClaimCard;
