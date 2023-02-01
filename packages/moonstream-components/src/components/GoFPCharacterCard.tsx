import React from "react";
import { Flex, Center, Text } from "@chakra-ui/react";

const CharacterCard = ({ tokenId }: { tokenId: number }) => {
  return (
    <Flex
      flexDirection="column"
      w="80px"
      h="100px"
      rounded="lg"
      borderWidth="3px"
      borderColor="#FFFFFF"
      borderRadius="10px"
      alignItems="center"
    >
      <Center
        w="63px"
        h="63px"
        borderWidth="1px"
        borderColor="#FFFFFF"
        borderRadius="50%"
        mt="5px"
      >
        <Text>{tokenId}</Text>
      </Center>
    </Flex>
  );
};

export default CharacterCard;
