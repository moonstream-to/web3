import React from "react";
import { Flex, HStack } from "@chakra-ui/react";
import { StageMetadata } from "./GoFPTypes";
import PathCard from "./GoFPPathCard";

const StagePanel = ({
  stageMetadata,
  onDrop,
  id,
}: {
  stageMetadata: StageMetadata;
  onDrop: (item: any) => void;
  id: number;
}) => {
  return (
    <Flex flexDirection="column" pb={3}>
      {/* <Text fontSize="md">{stageMetadata.lore}</Text> */}
      <br /> <br />
      <HStack>
        {stageMetadata.paths.map((path, idx) => {
          return (
            <PathCard
              accept={
                stageMetadata.isCurrent
                  ? idx === 0
                    ? "Frodo"
                    : ["Frodo", "character"]
                  : "none"
              }
              key={idx}
              id={`card-${id}-${idx}`}
              pathMetadata={path}
              onDrop={onDrop}
            ></PathCard>
          );
        })}
      </HStack>
    </Flex>
  );
};

export default StagePanel;
