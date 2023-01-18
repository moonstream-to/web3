import React from "react";
import { Flex, Center, Text, HStack } from "@chakra-ui/react";
import { StageMetadata, PathStatus } from "./GoFPTypes";
import PathCard from "./GoFPPathCard";

const StagePanel = ({
  stageMetadata,
  stageIdx,
  generatePathId,
}: {
  stageMetadata: StageMetadata;
  stageIdx: number;
  generatePathId: any;
}) => {
  const getPathStatus = (stageIdx: number, pathIdx: number) => {
    if (stageIdx > 1) {
      return PathStatus.undecided;
    } else {
      if (pathIdx - stageIdx == 0) return PathStatus.correct;
      else return PathStatus.incorrect;
    }
  };

  return (
    <Flex flexDirection="column" pb={10} zIndex={1}>
      <Text fontSize="md" fontWeight="bold" pb={5}>
        {stageMetadata.lore}
      </Text>
      <br /> <br />
      <Flex flexDirection="row" alignItems="center">
        {stageMetadata.paths.map((path, pathIdx) => {
          return (
            <Center key={pathIdx}>
              <PathCard
                pathMetadata={path}
                status={getPathStatus(stageIdx, pathIdx)}
                pathId={generatePathId(stageIdx, pathIdx)}
              ></PathCard>
            </Center>
          );
        })}
      </Flex>
    </Flex>
  );
};

export default StagePanel;
