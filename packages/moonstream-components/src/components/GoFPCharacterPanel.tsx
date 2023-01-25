import React from "react";
import {
  Flex,
  Center,
  Text,
  HStack,
  Accordion,
  AccordionItem,
  AccordionPanel,
  AccordionButton,
  AccordionIcon,
  Image,
  Button,
} from "@chakra-ui/react";
import { StageMetadata, PathStatus } from "./GoFPTypes";
import { SessionMetadata } from "./GoFPTypes";
import { UseMutationResult } from "react-query";

const CharacterPanel = ({
  sessionMetadata,
  setApproval,
  stakeTokens,
  unstakeTokens,
}: {
  sessionMetadata: SessionMetadata;
  setApproval: UseMutationResult<unknown, unknown, void, unknown>;
  stakeTokens: UseMutationResult<unknown, unknown, void, unknown>;
  unstakeTokens: UseMutationResult<unknown, unknown, void, unknown>;
}) => {
  return (
    <Flex
      backgroundColor="#353535"
      border="4px solid white"
      borderRadius="20px"
      w="400px"
      px={4}
      flexDirection="column"
    >
      <Text>{sessionMetadata.title}</Text>
      <Button colorScheme="yellow" onClick={() => setApproval.mutate()}>
        Set Approval
      </Button>
      <Button colorScheme="green" onClick={() => stakeTokens.mutate()}>
        Stake Tokens
      </Button>
      <Button colorScheme="red" onClick={() => unstakeTokens.mutate()}>
        Unstake Tokens
      </Button>
    </Flex>
  );
};

export default CharacterPanel;
