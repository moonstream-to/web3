import React from "react";
import { Flex, Image, Button } from "@chakra-ui/react";
import { PathMetadata } from "./GoFPTypes";

const PathCard = ({ pathMetadata }: { pathMetadata: PathMetadata }) => {
  return (
    <Flex flexDirection="column">
      <Image src={pathMetadata.imageUrl} h="200px" w="200px"></Image>
      {/* <Button bg="gray">Choose</Button> */}
    </Flex>
  );
};

export default PathCard;
