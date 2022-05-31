import React from "react";
import { chakra, Flex, Box } from "@chakra-ui/react";

const Metadata = ({ metadata, ...props }: { metadata: any }) => {
  return (
    <Flex
      zIndex={10}
      h="100%"
      {...props}
      direction="column"
      borderRadius={"lg"}
    >
      <Box
        borderRadius={"lg"}
        h="100%"
        w="100%"
        minW="120px"
        id="img"
        m={0}
        p={0}
        backgroundPosition="center"
        bgImage={metadata?.image ?? "none"}
        backgroundSize="contain"
        backgroundRepeat={"no-repeat"}
      ></Box>
      <chakra.span>{metadata?.name}</chakra.span>
      <chakra.span>{metadata?.description}</chakra.span>
    </Flex>
  );
};

export default chakra(Metadata);
