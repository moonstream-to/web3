import React from "react";
import {
  chakra,
  Flex,
  Heading,
  UnorderedList,
  ListItem,
} from "@chakra-ui/react";

const _DropList = ({ contractResource, children, ...props }) => {
  return (
    <Flex
      borderRadius={"md"}
      bgColor="blue.800"
      w="100%"
      direction={"column"}
      p={4}
      mt={2}
      textColor={"gray.300"}
      {...props}
    >
      <Heading as={"h2"} fontSize="lg" mt={2} borderBottomWidth="2px">
        {contractResource.title ?? "unnamed dropper contract"}
      </Heading>
      <Heading as={"h3"} fontSize="md">
        {contractResource.description ?? "this contract has no description"}
      </Heading>
      <Flex w="100%" direction={["row", null]} flexWrap="wrap">
        <Flex
          direction={"row"}
          flexGrow={1}
          flexBasis={"200px"}
          wordBreak="break-word"
        >
          <Flex
            mt={2}
            direction={"row"}
            minW="200px"
            flexWrap={"wrap"}
            w="100%"
            bgColor={"blue.1100"}
            borderRadius="md"
            px={2}
            // pt={4}
          >
            <UnorderedList fontSize={"sm"}>
              <ListItem>
                Contract: <code>{contractResource.address}</code>
              </ListItem>
              <ListItem>chain: {contractResource.blockchain}</ListItem>
            </UnorderedList>
          </Flex>
        </Flex>
      </Flex>
      {children && children}
    </Flex>
  );
};

const DropList = chakra(_DropList);
export default DropList;
