import React from "react";
import { Flex, Text, HStack } from "@chakra-ui/react";
import { StageMetadata } from "./GoFPTypes";
import PathCard from "./GoFPPathCard";

const StagePanel = ({ stageMetadata }: { stageMetadata: StageMetadata }) => {
  return (
    <Flex flexDirection="column" pb={10}>
      <Text fontSize="md" pb={5}>
        {stageMetadata.lore}
      </Text>
      <br /> <br />
      <HStack>
        {stageMetadata.paths.map((path, idx) => {
          return <PathCard key={idx} pathMetadata={path}></PathCard>;
        })}
      </HStack>
    </Flex>
  );
};

export default StagePanel;
