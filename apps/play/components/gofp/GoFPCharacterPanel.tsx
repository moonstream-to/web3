import React from "react";
import { Flex, Box, SimpleGrid, Text, Button } from "@chakra-ui/react";
// import { SessionMetadata } from "./GoFPTypes";
import { UseMutationResult } from "react-query";
import CharacterCard from "./GoFPCharacterCard";

const CharacterPanel = ({
  // sessionMetadata,
  ownedTokens,
  stakedTokens,
  tokenMetadata,
  path,
  setApproval,
  stakeTokens,
  unstakeTokens,
  choosePath,
}: {
  // sessionMetadata: SessionMetadata;
  ownedTokens: number[];
  stakedTokens: number[];
  tokenMetadata: any;
  path: number;
  setApproval: UseMutationResult<unknown, unknown, void, unknown>;
  stakeTokens: UseMutationResult<unknown, unknown, number[], unknown>;
  unstakeTokens: UseMutationResult<unknown, unknown, number[], unknown>;
  choosePath: UseMutationResult<unknown, unknown, number, unknown>;
}) => {
  const tokenState: Map<number, boolean> = new Map<number, boolean>();
  ownedTokens.concat(stakedTokens).forEach((tokenId) => {
    tokenState.set(tokenId, false);
  });
  const onSelect = (tokenId: number, selected: boolean) => {
    tokenState.set(tokenId, selected);
  };
  const getSelectedOwnedTokens = () => {
    return ownedTokens.filter((tokenId) => {
      return tokenState.get(tokenId) == true;
    });
  };
  const getSelectedStakedTokens = () => {
    return stakedTokens.filter((tokenId) => {
      return tokenState.get(tokenId) == true;
    });
  };
  const createCharacterGrid = (chars: number[]) => {
    return (
      <SimpleGrid columns={3} spacing={5}>
        {chars.map((token) => {
          return (
            <CharacterCard
              key={token}
              tokenId={token}
              tokenImage={tokenMetadata[token].image}
              tokenName={tokenMetadata[token].name}
              onSelect={onSelect}
            />
          );
        })}
      </SimpleGrid>
    );
  };
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
        {createCharacterGrid(stakedTokens)}
        <Flex mt={10} flexDirection="column">
          <Button
            mt={10}
            colorScheme="blue"
            onClick={() => choosePath.mutate(path)}
          >
            Choose Path {path}
          </Button>
          <Button
            colorScheme="red"
            onClick={() => unstakeTokens.mutate(getSelectedStakedTokens())}
          >
            Unstake Tokens
          </Button>
        </Flex>
      </Box>
      <Box>
        <Text fontSize="md" py={6}>
          Available Characters
        </Text>
        {createCharacterGrid(ownedTokens)}
        <Flex mt={10} flexDirection="column">
          <Button colorScheme="yellow" onClick={() => setApproval.mutate()}>
            Set Approval
          </Button>
          <Button
            colorScheme="green"
            onClick={() => stakeTokens.mutate(getSelectedOwnedTokens())}
          >
            Stake Tokens
          </Button>
        </Flex>
      </Box>
    </Flex>
  );
};

export default CharacterPanel;
