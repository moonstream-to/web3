import React from "react";
import { Flex, Center, Text } from "@chakra-ui/react";

const CharacterCard = ({ tokenId }: { tokenId: number }) => {
  return (
    <Flex
      flexDirection="column"
      w="80px"
      h="100px"
      rounded="lg"
      borderWidth="2px"
      borderColor="#BFBFBF"
      borderRadius="10px"
      alignContent="center"
    >
      <Center>
        <Text>{tokenId}</Text>
      </Center>
    </Flex>
  );
};

export default CharacterCard;
