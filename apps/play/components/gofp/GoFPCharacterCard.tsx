import React, { useState, useEffect } from "react";
import { Flex, Box, Text } from "@chakra-ui/react";

const CharacterCard = ({
  tokenId,
  tokenImage,
  tokenName,
  tokenPath,
  tokenGuard,
  onSelect,
}: {
  tokenId: number;
  tokenImage: string;
  tokenName: string;
  tokenPath?: number;
  tokenGuard?: boolean;
  onSelect: (tokenId: number, selected: boolean) => void;
}) => {
  const [selected, setSelected] = useState<boolean>(false);

  useEffect(() => {
    onSelect(tokenId, selected);
  });

  const assigned: boolean = !!tokenPath && tokenPath > 0;
  const played: boolean = !!tokenGuard;

  const displayStatus = () => {
    var statusText = "Available";
    if (assigned) {
      statusText = `Assigned to path ${tokenPath}`;
    } else if (played) {
      statusText = "Already played";
    } else if (typeof tokenPath != "undefined") {
      statusText = "Choose a path";
    }
    return (
      <Text
        fontSize="8px"
        pt={1}
        px={1}
        textColor={tokenGuard ? "#EE8686" : undefined}
      >
        {statusText}
      </Text>
    );
  };

  return (
    <Flex
      flexDirection="column"
      w="90px"
      h="130px"
      mx={1}
      rounded="lg"
      borderWidth={selected ? "4px" : "1px"}
      borderColor={(assigned || played) && !selected ? "#BFBFBF" : "#FFFFFF"}
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
        opacity={assigned || played ? 0.5 : 1.0}
      />
      <Text fontSize="12px" pt={1} px={1}>
        {tokenName || tokenId}
      </Text>
      {displayStatus()}
    </Flex>
  );
};

export default CharacterCard;
