import React, { useState } from "react";
import { Flex, Box, Text } from "@chakra-ui/react";

const CharacterCard = ({
  tokenId,
  tokenImage,
  tokenName,
  onSelect,
}: {
  tokenId: number;
  tokenImage: string;
  tokenName: string;
  onSelect: (tokenId: number, selected: boolean) => void;
}) => {
  const [selected, setSelected] = useState<boolean>(false);
  return (
    <Flex
      flexDirection="column"
      w="80px"
      h="100px"
      mx={2}
      rounded="lg"
      borderWidth={selected ? "4px" : "1px"}
      borderColor="#FFFFFF"
      borderRadius="10px"
      alignItems="center"
      textAlign="center"
      onClick={() => {
        const newVal = !selected;
        setSelected(newVal);
        onSelect(tokenId, newVal);
      }}
    >
      <Box
        w="63px"
        h="63px"
        borderWidth="1px"
        borderColor="#FFFFFF"
        borderRadius="50%"
        mt="5px"
        backgroundImage={tokenImage}
        backgroundPosition="center"
        backgroundSize="contain"
      />
      <Text fontSize="xs" px={1}>
        {tokenName || tokenId}
      </Text>
    </Flex>
  );
};

export default CharacterCard;
