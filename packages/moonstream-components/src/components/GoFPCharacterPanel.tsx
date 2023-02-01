import React from "react";
import { Flex, Box, Text, Button } from "@chakra-ui/react";
// import { SessionMetadata } from "./GoFPTypes";
import { UseMutationResult } from "react-query";
import CharacterCard from "./GoFPCharacterCard";

const CharacterPanel = ({
  // sessionMetadata,
  ownedTokens,
  stakedTokens,
  path,
  setApproval,
  stakeTokens,
  unstakeTokens,
  choosePath,
}: {
  // sessionMetadata: SessionMetadata;
  ownedTokens: number[];
  stakedTokens: number[];
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
      h="700px"
      px={4}
      flexDirection="column"
    >
      <Box>
        <Text fontSize="md" py={6}>
          Staked Characters
        </Text>
        {stakedTokens.map((token) => {
          return <CharacterCard key={token} tokenId={token}></CharacterCard>;
        })}
        <Button
          mt={10}
          colorScheme="blue"
          onClick={() => choosePath.mutate(path)}
        >
          Choose Path {path}
        </Button>
      </Box>
      <Box>
        <Text fontSize="md" py={6}>
          Available Characters
        </Text>
        {ownedTokens.map((token) => {
          return <CharacterCard key={token} tokenId={token}></CharacterCard>;
        })}
        <Flex mt={10} flexDirection="column">
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
      </Box>
    </Flex>
  );
};

export default CharacterPanel;
