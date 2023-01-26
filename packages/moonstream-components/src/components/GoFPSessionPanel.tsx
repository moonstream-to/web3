import React, { useEffect, useState } from "react";
import { Flex, Center, Text } from "@chakra-ui/react";
import { SessionMetadata } from "./GoFPTypes";
import StagePanel from "./GoFPStagePanel";
import { UseQueryResult } from "react-query";
import Connections from "../../../../apps/play/components/Connections";
import ResizeObserver from "rc-resize-observer";

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
  //   // return () => window.removeEventListener("scroll");
  // });
  const [connectionsData, setConnectionsData] = useState({
    links: [],
    futureLinks: [],
  });
  useEffect(() => {
    if (correctPaths.data && currentStage.data && sessionMetadata.stages) {
      const correctPathsZB = correctPaths.data.map((path: number) => path - 1);
      const currentStageZB = currentStage.data - 1;
      const links = [];
      for (let i = 0; i < correctPathsZB.length - 1; i += 1) {
        links.push({
          source: generatePathId(i, correctPathsZB[i]),
          target: generatePathId(i + 1, correctPathsZB[i + 1]),
        });
      }
      const lastDoor = generatePathId(
        correctPathsZB.length - 1,
        correctPathsZB[correctPathsZB.length - 1]
      );
      const newFutureStages: { sources: string[]; targets: string[] }[] = [];
      for (
        let i = currentStageZB - 1;
        i < sessionMetadata.stages.length - 1;
        i += 1
      ) {
        if (i === -1) {
          continue;
        }
        const futureStage: { sources: string[]; targets: string[] } = {
          sources: [],
          targets: [],
        };
        for (let j = 0; j < sessionMetadata.stages[i].paths.length; j += 1) {
          futureStage.sources.push(generatePathId(i, j));
        }
        for (
          let j = 0;
          j < sessionMetadata.stages[i + 1].paths.length;
          j += 1
        ) {
          futureStage.targets.push(generatePathId(i + 1, j));
        }
        newFutureStages.push(futureStage);
      }
      if (currentStageZB > 0) {
        newFutureStages[0].sources = newFutureStages[0].sources.filter(
          (s) => s === lastDoor
        );
      }
      setConnectionsData({ links, futureLinks: newFutureStages });
    }
  }, [correctPaths, currentStage, sessionMetadata]);

  const [containerWidth, setContainerWidth] = useState(0);

  const handleResize = ({ width }: { width: number }) => {
    setContainerWidth(width);
  };

  return (
    <ResizeObserver onResize={handleResize}>
      <Flex
        flexDirection="column"
        onScroll={() => {
          console.log("scrolling");
        }}
        position="relative"
      >
        <Connections
          links={connectionsData.links}
          futureStages={connectionsData.futureLinks}
          offsets={{ top: { x: 0, y: 0.055 }, bottom: { x: 0, y: -0.055 } }}
          width={containerWidth}
        />
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
          const correctPath = correctPaths.data
            ? correctPaths.data[stageIdx]
            : 0;
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
    </ResizeObserver>
  );
};

export default SessionPanel;
