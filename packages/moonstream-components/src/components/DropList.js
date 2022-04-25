import React from "react";
import { chakra, Flex, Text, Stack, Heading } from "@chakra-ui/react";
import DropCard from "./DropCard";

const DropList = ({ drops }) => {
  return (
    <Flex
      mt={10}
      id="DropListContainer"
      bgColor="gray.300"
      borderRadius={"md"}
      mx={["20px", "7%", null]}
      maxWidth="1337px"
      px={"20px"}
      py={"10px"}
      direction="column"
    >
      <Heading py={2}> Your drops list</Heading>
      <Stack direction={"column"} spacing={2} flexGrow={1}>
        {drops?.map((drop) => (
          <DropCard key={drop.id} drop={drop} />
        ))}
      </Stack>
    </Flex>
  );
};

export default DropList;
