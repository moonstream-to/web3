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
import { useDropperContract } from "../core/hooks/dropper";

const _ClaimCard = ({ drop, children, ...props }) => {
  const web3Provider = useContext(Web3Context);

  const claimer = useClaim({
    dropperAddress: drop.dropper_contract_address,
    ctx: web3Provider,
    claimId: drop.dropper_claim_id,
    userAccess: true,
    claimantAddress: web3Provider.account,
  });

  const dropperContract = useDropperContract({
    dropperAddress: drop.dropper_contract_address,
    ctx: web3Provider,
    claimId: drop.claim_id,
  });

  if (
    claimer.claimStatus?.data &&
    (claimer.claimStatus?.data.status > 0 ||
      claimer.claimStatus?.data.claim[0] == "0")
  )
    if (
      claimer.isLoadingClaim ||
      dropperContract.contractState.data?.isLoading ||
      dropperContract.claimState.isLoading ||
      claimer.signature.isLoading
    )
      return <Spinner />;

  return (
    <Flex
      bgColor="#353535"
      border="1px solid white"
      borderRadius="20px"
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
            bgColor={"#232323"}
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
              <ListItem>
                Reward Type:{" "}
                <code>{dropperContract.claimState.data?.claim.tokenType}</code>
              </ListItem>
              <ListItem>
                Reward address:{" "}
                <code>
                  {dropperContract.claimState.data?.claim.tokenAddress}
                </code>
              </ListItem>
              <ListItem>
                Token id:{" "}
                <code>{dropperContract.claimState.data?.claim.tokenId}</code>
              </ListItem>
              <ListItem>claimd id: {drop.claim_id}</ListItem>
            </UnorderedList>
          </Flex>
        </Flex>
        {/* <Flex
          //TODO: add claim metadata here
          flexGrow={1}
          m={2}
          h="auto"
          flexBasis={"220px"}
          bgColor={"red.500"}
          borderRadius="md"
        ></Flex> */}
      </Flex>
      <Flex direction={"row"} justifyContent="space-evenly" pt={4}>
        <Button
          variant={"orangeOutline"}
          size="xl"
          borderWidth="3px"
          isLoading={dropperContract.claimWeb3Drop.isLoading}
          isDisabled={!dropperContract.claimState.data?.canClaim}
          onClick={() =>
            dropperContract.claimWeb3Drop.mutate({
              message: claimer.signature.data?.signature,
              blockDeadline: claimer.signature.data?.block_deadline,
              claimId: claimer.signature.data?.claim_id,
              amount: claimer.signature.data?.amount,
            })
          }
        >
          {dropperContract.claimState.data?.canClaim
            ? "Claim now"
            : "Already claimed"}
        </Button>
      </Flex>
      {children && children}
    </Flex>
  );
};
const ClaimCard = chakra(_ClaimCard);
export default ClaimCard;
