import React from "react";
import { Flex, Center } from "@chakra-ui/react";
import { StageMetadata, PathStatus } from "./GoFPTypes";
import PathCard from "./GoFPPathCard";

const StagePanel = ({
  stageMetadata,
  stageIdx,
  completed,
  correctPath,
  generatePathId,
  setSelectedStage,
  setSelectedPath,
}: {
  stageMetadata: StageMetadata;
  stageIdx: number;
  completed: boolean;
  correctPath: number;
  generatePathId: any;
  setSelectedStage: React.Dispatch<React.SetStateAction<number>>;
  setSelectedPath: React.Dispatch<React.SetStateAction<number>>;
}) => {
  const getPathStatus = (pathIdx: number) => {
    if (completed) {
      if (pathIdx + 1 == correctPath) {
        return PathStatus.correct;
      } else {
        return PathStatus.incorrect;
      }
    } else {
      return PathStatus.undecided;
    }
  };

  return (
    <Flex
      flexDirection="column"
      pb={10}
      zIndex={1}
      onClick={() => {
        setSelectedStage(stageIdx + 1);
      }}
    >
      {/* <Text fontSize="md" fontWeight="bold" pb={5}>
        {stageMetadata.lore}
      </Text>
      <br /> <br /> */}
      <Flex flexDirection="row" alignItems="center">
        {stageMetadata.paths.map((path, pathIdx) => {
          return (
            <Center key={pathIdx}>
              <PathCard
                pathMetadata={path}
                status={getPathStatus(pathIdx)}
                pathId={generatePathId(stageIdx, pathIdx)}
                setSelectedPath={() => {
                  console.log("Selecting path ", pathIdx + 1);
                  setSelectedPath(pathIdx + 1);
                }}
              ></PathCard>
            </Center>
          );
        })}
      </Flex>
    </Flex>
  );
};

export default StagePanel;
