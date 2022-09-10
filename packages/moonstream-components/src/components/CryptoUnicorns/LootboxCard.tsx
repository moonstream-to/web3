import React, { useState } from "react";
import {
  Flex,
  Image,
  Text,
  chakra,
  Spacer,
  VStack,
  Box,
} from "@chakra-ui/react";

const _LootboxCard = ({
  displayName,
  imageUrl,
  lootboxBalance,
  showQuantity = true,
  isVideo = false,
  ...props
}: {
  displayName: string;
  imageUrl: string;
  lootboxBalance: number;
  showQuantity?: boolean;
  isVideo?: boolean;
}) => {
  return (
    <Flex {...props} pb={10}>
      <VStack maxW="250" border="solid" borderColor="#373E9B" borderRadius="lg">
        <Image
          src={imageUrl}
          as={isVideo ? "video" : undefined}
          loading="lazy"
          w={250}
          borderRadius="sm"
          alt="CU Inventory Item"
        />
        {/* <video autoPlay loop><source src={imageUrl}></source></video> */}
        <Box w="100%" px={2} justifyContent="left" pb={0}>
          <Text fontSize="md">{displayName}</Text>
          {showQuantity && (
            <Flex fontSize="sm" w="100%">
              <Text>Quantity</Text>
              <Spacer />
              <Text>{lootboxBalance}</Text>
            </Flex>
          )}
        </Box>
      </VStack>
    </Flex>
  );
};

const LootboxCard = chakra(_LootboxCard);
export default LootboxCard;
