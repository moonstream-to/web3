import React, { useState } from "react";
import {
  Flex,
  HStack,
  Image,
  Text,
  Input,
  Button,
  chakra,
  Spacer,
  VStack,
  Heading,
  Container,
  Box,
} from "@chakra-ui/react";

const _LootboxCard = ({
  displayName,
  imageUrl,
  lootboxBalance,
  ...props
}: {
  displayName: string;
  imageUrl: string;
  lootboxBalance: number;
}) => {
  const [lootboxCount, setLootboxCount] = useState("");
  const [countToStash, setCountToStash] = useState("");

  // const stashLootboxes = () => {

  // };

  return (
    <Flex {...props} pb={10}>
      <VStack maxW="250" border="solid" borderColor="#373E9B" borderRadius="lg">
        <Image
          src={imageUrl}
          w={250}
          h={250}
          m={"2px"}
          alt="CU Common Lootbox"
        />
        <Box w="100%" px={2} justifyContent="left">
          <Text fontSize="md">{displayName}</Text>
          <Flex fontSize="sm" w="100%" pb={6}>
            <Text>Quantity</Text>
            <Spacer />
            <Text>{lootboxBalance}</Text>
          </Flex>
          {/* <Box pb={3}>
            <Input
              bgColor="transparent"
              borderColor="gray.100"
              borderWidth="1px"
              rounded="md"
              size={"sm"}
              fontSize={"md"}
              m={0}
              mb={2}
              p={2}
              placeholder="Enter amount to stash"
              value={countToStash}
              onChange={(event) => {
                const count = event.target.value;
                setCountToStash(count);
                console.log(`Stashing ${count} ${lootboxType} lootboxes.`);
              }}
            />
            <Button
              w="100%"
              h="32px"
              m={0}
              rounded="md"
              size="md"
              bgColor={lootboxBalance > 0 ? "#FE9A67" : "#79828D"}
              disabled={lootboxBalance <= 0}
              textColor="white"
              fontSize="lg"
              fontWeight="bold"
              onClick={() => {
                console.log(`Stashing ${countToStash} lootboxes.`);
              }}
            >
              Stash!
            </Button>
          </Box> */}
        </Box>
      </VStack>
    </Flex>
  );
};

const LootboxCard = chakra(_LootboxCard);
export default LootboxCard;
