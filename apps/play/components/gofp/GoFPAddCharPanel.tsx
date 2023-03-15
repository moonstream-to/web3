import React from "react";
import { Flex, Box, SimpleGrid, Text, Button } from "@chakra-ui/react";
// import { SessionMetadata } from "./GoFPTypes";
import { UseMutationResult } from "react-query";
import CharacterCard from "./GoFPCharacterCard";
import { BsArrowLeftShort } from "react-icons/bs";

const AddCharPanel = ({
  ownedTokens,
  tokenMetadata,
  tokenGuards,
  // setApproval,
  stakeTokens,
  setShowActive,
}: {
  ownedTokens: number[];
  tokenMetadata: any;
  tokenGuards?: Map<number, boolean>;
  setApproval: UseMutationResult<unknown, unknown, void, unknown>;
  stakeTokens: UseMutationResult<unknown, unknown, number[], unknown>;
  setShowActive: React.Dispatch<React.SetStateAction<boolean>>;
}) => {
  const tokenState: Map<number, boolean> = new Map<number, boolean>();
  ownedTokens.forEach((tokenId) => {
    tokenState.set(tokenId, false);
  });
  const onSelect = (tokenId: number, selected: boolean) => {
    tokenState.set(tokenId, selected);
  };
  return (
    <Box py={6}>
      <Flex alignItems="center" onClick={() => setShowActive(true)}>
        <BsArrowLeftShort size="20px" />
        <Text fontSize="md">Assign Characters</Text>
      </Flex>
      <Text fontSize="lg" fontWeight="bold" pt={4}>
        All Characters
      </Text>
      <Text fontSize="sm" pt={4}>
        Select characters and send them into session to start playing.
      </Text>
      <SimpleGrid columns={3} spacing={4} pt={4}>
        {ownedTokens.map((token) => {
          return (
            <CharacterCard
              key={token}
              tokenId={token}
              tokenImage={tokenMetadata[token].image}
              tokenName={tokenMetadata[token].name}
              tokenGuard={tokenGuards?.get(token)}
              onSelect={onSelect}
            />
          );
        })}
      </SimpleGrid>
      <Flex mt={6} flexDirection="column">
        <Button
          w="100%"
          backgroundColor="#F56646"
          rounded="lg"
          onClick={async () => {
            await stakeTokens.mutate(
              ownedTokens.filter((tokenId) => tokenState.get(tokenId) == true)
            );
            setShowActive(true);
          }}
        >
          Play
        </Button>
      </Flex>
    </Box>
  );
};

export default AddCharPanel;
