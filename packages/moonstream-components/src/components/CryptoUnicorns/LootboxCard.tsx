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
  Box
} from "@chakra-ui/react";

const _LootboxCard = ({
  lootboxType,
  imageUrl,
  lootboxBalance,
  ...props
}: {
  lootboxType: string;
  imageUrl: string;
  lootboxBalance: number;
}) => {
  const [lootboxCount, setLootboxCount] = useState(0);
  const [countToStash, setCountToStash] = useState(0);

  // const stashLootboxes = () => {

  // };

  return (
    <Flex {...props} pb={10} px={10}>
      <VStack maxW="220" border="solid" borderColor="#373E9B" borderRadius="md">
        <Image src={imageUrl} w={220} h={220} alt="CU Common Lootbox" />
        <Box w="100%" px={2} justifyContent="left">
          <Text fontSize="lg">{lootboxType} Lootbox</Text>
          <Flex fontSize="sm" w="100%" pb={6}>
            {lootboxBalance > 0 ? (
              <>
                <Text>Quantity</Text>
                <Spacer />
                <Text>{lootboxBalance}</Text>
              </>
            ) : (
              <Text>You have no {lootboxType} lootboxes.</Text>
            )}
          </Flex>
          <Box pb={3}>
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
              onClick={() => {}}
            >
              Stash!
            </Button>
          </Box>
        </Box>
      </VStack>
      {/* <HStack>
        <Image src={imageUrl} w={100} h={100} alt="CU Common Lootbox" />
        <Flex>
          <Text fontSize="xl">
            I have {lootboxCount} {lootboxType}.
          </Text>
          &nbsp;
          <Text fontSize="xl">
            I would like to stash
            <Input
              textColor={"blue.900"}
              size={"sm"}
              fontSize={"md"}
              variant={"outline"}
              mx={2}
              w="40px"
            />
            lootboxes into my game.
          </Text>
          <br />
          <Spacer />
          <Button
            mx={4}
            size="md"
            variant="outline"
            w="220px"
            colorScheme={"orange"}
            onClick={() => {}}
          >
            Stash!
          </Button>
        </Flex>
      </HStack> */}
    </Flex>
  );
};

const LootboxCard = chakra(_LootboxCard);
export default LootboxCard;
