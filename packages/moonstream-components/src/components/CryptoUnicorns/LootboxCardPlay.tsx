import React from "react";
import { Flex, Image, Text, chakra, Spacer, VStack } from "@chakra-ui/react";

const _LootboxCard = ({
  displayName,
  imageUrl,
  lootboxBalance,
  showQuantity = true,
  isVideo = false,
  grayedOut = false,
  ...props
}: {
  displayName: string;
  imageUrl: string;
  lootboxBalance: number;
  showQuantity?: boolean;
  isVideo?: boolean;
  grayedOut?: boolean;
}) => {
  return (
    <Flex {...props} p="20px" bg="#353535" borderRadius="20px" maxW="290px">
      <VStack maxW="250">
        <Image
          src={imageUrl}
          as={isVideo ? "video" : undefined}
          filter={grayedOut ? "grayscale(100%)" : undefined}
          opacity={grayedOut ? "0.3" : undefined}
          loading="lazy"
          w="100%"
          borderRadius="10px"
          border="1px solid #4D4D4D"
          alt="CU Inventory Item"
        />
        <Flex
          direction="column"
          justifyContent="space-between"
          w="100%"
          h="80px"
          px={2}
          pb={0}
        >
          <Text fontSize="md" fontWeight="700">
            {displayName}
          </Text>
          {showQuantity && (
            <Flex fontSize="sm" w="100%">
              <Text>Quantity</Text>
              <Spacer />
              <Text>{lootboxBalance}</Text>
            </Flex>
          )}
        </Flex>
      </VStack>
    </Flex>
  );
};

const LootboxCard = chakra(_LootboxCard);
export default LootboxCard;
