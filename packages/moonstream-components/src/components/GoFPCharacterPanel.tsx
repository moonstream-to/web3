import React from "react";
import { Flex, Text, Button } from "@chakra-ui/react";
import { SessionMetadata } from "./GoFPTypes";
import { UseMutationResult } from "react-query";

const CharacterPanel = ({
  sessionMetadata,
  path,
  setApproval,
  stakeTokens,
  unstakeTokens,
  choosePath,
}: {
  sessionMetadata: SessionMetadata;
  path: number;
  setApproval: UseMutationResult<unknown, unknown, void, unknown>;
  stakeTokens: UseMutationResult<unknown, unknown, void, unknown>;
  unstakeTokens: UseMutationResult<unknown, unknown, void, unknown>;
  choosePath: UseMutationResult<unknown, unknown, number, unknown>;
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
      <Button colorScheme="gray" onClick={() => choosePath.mutate(path)}>
        Choose Path {path}
      </Button>
    </Flex>
  );
};

export default CharacterPanel;
