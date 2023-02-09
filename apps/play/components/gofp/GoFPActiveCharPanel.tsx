import React from "react";
import {
  Flex,
  Box,
  SimpleGrid,
  Text,
  Button,
  Spacer,
  Center,
} from "@chakra-ui/react";
import { UseMutationResult } from "react-query";
import CharacterCard from "./GoFPCharacterCard";
import { AiOutlinePlus } from "react-icons/ai";

const ActiveCharPanel = ({
  activeTokens,
  tokenMetadata,
  path,
  unstakeTokens,
  choosePath,
  setShowActive,
}: {
  activeTokens: number[];
  tokenMetadata: any;
  path: number;
  unstakeTokens: UseMutationResult<unknown, unknown, number[], unknown>;
  choosePath: UseMutationResult<unknown, unknown, number, unknown>;
  setShowActive: React.Dispatch<React.SetStateAction<boolean>>;
}) => {
  const tokenState: Map<number, boolean> = new Map<number, boolean>();
  activeTokens.forEach((tokenId) => {
    tokenState.set(tokenId, false);
  });
  const onSelect = (tokenId: number, selected: boolean) => {
    tokenState.set(tokenId, selected);
  };
  return (
    <Box py={6}>
      <Flex>
        <Text fontSize="lg" fontWeight="bold">
          Assign Characters
        </Text>
        <Spacer />
        <Flex alignItems="center" onClick={() => setShowActive(false)}>
          <AiOutlinePlus size="10px" />
          <Text fontSize="sm">Add More</Text>
        </Flex>
      </Flex>
      <SimpleGrid columns={3} spacing={5} pt={4}>
        {activeTokens.map((token) => {
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
      <Flex mt={6} flexDirection="column">
        <Button
          width="100%"
          backgroundColor="transparent"
          borderWidth="1px"
          borderColor="#BFBFBF"
          borderRadius="18px"
          textColor="#BFBFBF"
          onClick={() => choosePath.mutate(path)}
        >
          Choose Path {path}
        </Button>
        <Center>
          <Text>or&nbsp;</Text>
          <Text
            color="#EE8686"
            onClick={() =>
              unstakeTokens.mutate(
                activeTokens.filter(
                  (tokenId) => tokenState.get(tokenId) == true
                )
              )
            }
          >
            remove characters from session
          </Text>
        </Center>
      </Flex>
    </Box>
  );
};

export default ActiveCharPanel;
