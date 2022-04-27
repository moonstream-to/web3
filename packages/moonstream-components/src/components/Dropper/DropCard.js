import React from "react";
import { chakra, Flex, Heading, Button } from "@chakra-ui/react";
const DropCard = ({ drop }) => {
  return (
    <Flex
      bgColor="blue.600"
      borderRadius="md"
      h="80px"
      px={4}
      py={2}
      flexGrow={1}
      alignContent="baseline"
      justifyContent={"space-between"}
      alignItems="top"
      //   direction={"column"}
    >
      <Flex direction={"column"}>
        <Heading
          fontWeight={600}
          textColor="gray.100"
          h="min-content"
          as="h3"
          fontSize={"md"}
        >
          {drop.title}
        </Heading>
        <chakra.span>{drop.description}</chakra.span>
      </Flex>
      <Button>Activate</Button>
      <Button>Deactivate</Button>
      <Button>Upload whitelist</Button>
    </Flex>
  );
};

export default DropCard;
