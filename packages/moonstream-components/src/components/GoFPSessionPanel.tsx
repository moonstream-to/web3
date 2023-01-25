import React, { useEffect } from "react";
import { Flex, Center, Text } from "@chakra-ui/react";
import { SessionMetadata } from "./GoFPTypes";
import StagePanel from "./GoFPStagePanel";
import Xarrow, { useXarrow } from "react-xarrows";
import { UseQueryResult } from "react-query";

const SessionPanel = ({
  sessionMetadata,
  currentStage,
  correctPaths,
  generatePathId,
  setSelectedStage,
}: {
  sessionMetadata: SessionMetadata;
  currentStage: UseQueryResult<number>;
  correctPaths: UseQueryResult<number[]>;
  generatePathId: any;
  setSelectedStage: React.Dispatch<React.SetStateAction<number>>;
}) => {
  // const updateXArrow = useXarrow();

  // useEffect(() => {
  //   window.addEventListener("scroll", () => {
  //     console.log("scrolling");
  //   });
  //   //return () => window.removeEventListener("scroll", updateXArrow);
  // });

  return (
    <Flex
      flexDirection="column"
      onScroll={() => {
        console.log("scrolling");
      }}
    >
      <Center>
        <Text fontSize="lg" pb={10}>
          {sessionMetadata.lore}
        </Text>
      </Center>
      {sessionMetadata.stages.map((stage, stageIdx) => {
        const stageNumber = stageIdx + 1;
        const completed = currentStage.data
          ? stageNumber < currentStage.data
          : false;
        const correctPath = correctPaths.data ? correctPaths.data[stageIdx] : 0;
        return (
          <Center key={stageIdx}>
            <StagePanel
              stageMetadata={stage}
              stageIdx={stageIdx}
              completed={completed}
              correctPath={correctPath}
              generatePathId={generatePathId}
              setSelectedStage={setSelectedStage}
            ></StagePanel>
          </Center>
        );
      })}
      {/* <Xarrow
        start={generatePathId(0, 0)}
        end={generatePathId(1, 1)}
        startAnchor="bottom"
        endAnchor="top"
        lineColor="#3BB563"
        path="grid"
        showHead={false}
        strokeWidth={3}
        zIndex={0}
      />
      <Xarrow
        start={generatePathId(1, 1)}
        end={generatePathId(2, 0)}
        startAnchor="bottom"
        endAnchor="top"
        lineColor="#BFBFBF"
        path="grid"
        dashness={true}
        showHead={false}
        strokeWidth={2}
        zIndex={0}
      />
      <Xarrow
        start={generatePathId(1, 1)}
        end={generatePathId(2, 1)}
        startAnchor="bottom"
        endAnchor="top"
        lineColor="#BFBFBF"
        path="grid"
        dashness={true}
        showHead={false}
        strokeWidth={2}
        zIndex={0}
      />
      <Xarrow
        start={generatePathId(1, 1)}
        end={generatePathId(2, 2)}
        startAnchor="bottom"
        endAnchor="top"
        lineColor="#BFBFBF"
        path="grid"
        dashness={true}
        showHead={false}
        strokeWidth={2}
        zIndex={0}
      />
      <Xarrow
        start={generatePathId(2, 0)}
        end={generatePathId(3, 0)}
        startAnchor="bottom"
        endAnchor="top"
        lineColor="#BFBFBF"
        path="grid"
        dashness={true}
        showHead={false}
        strokeWidth={2}
        zIndex={0}
      />
      <Xarrow
        start={generatePathId(2, 1)}
        end={generatePathId(3, 0)}
        startAnchor="bottom"
        endAnchor="top"
        lineColor="#BFBFBF"
        path="grid"
        dashness={true}
        showHead={false}
        strokeWidth={2}
        zIndex={0}
      />
      <Xarrow
        start={generatePathId(2, 2)}
        end={generatePathId(3, 0)}
        startAnchor="bottom"
        endAnchor="top"
        lineColor="#BFBFBF"
        path="grid"
        dashness={true}
        showHead={false}
        strokeWidth={2}
        zIndex={0}
      /> */}
    </Flex>
  );
};

export default SessionPanel;
