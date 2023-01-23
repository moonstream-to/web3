import React, { useState, useEffect } from "react";
import { Center, Flex, Text } from "@chakra-ui/react";
import { SessionMetadata } from "./GoFPTypes";
import StagePanel from "./GoFPStagePanel";
import Connections from "../../../../apps/play/components/Connections";
import ResizeObserver from "rc-resize-observer";

const SessionPanel = ({
  sessionMetadata,
  onDrop,
}: {
  sessionMetadata: SessionMetadata;
  onDrop: (item: any) => void;
}) => {
  const [currentStage, setCurrentStage] = useState(4);
  const [links, setLinks] = useState(new Map<string, string>());
  const [futureStages, setFutureStages] = useState<
    { sources: string[]; targets: string[] }[]
  >([]);
  const [containerWidth, setContainerWidth] = useState(0);

  useEffect(() => {
    const newLinks = new Map<string, string>();
    newLinks.set("card-0-1", "card-1-0");
    newLinks.set("card-1-0", "card-2-3");
    newLinks.set("card-2-3", "card-3-1");
    newLinks.set("card-3-1", "card-4-1");
    setLinks(newLinks);
    const lastDoor = "card-4-1";
    const extendedStages = sessionMetadata.stages
      .concat(sessionMetadata.stages)
      .concat(sessionMetadata.stages);
    const newFutureStages: { sources: string[]; targets: string[] }[] = [];
    for (let i = currentStage; i < extendedStages.length - 1; i += 1) {
      const futureStage: { sources: string[]; targets: string[] } = {
        sources: [],
        targets: [],
      };
      for (let j = 0; j < extendedStages[i].paths.length; j += 1) {
        futureStage.sources.push(`card-${i}-${[j]}`);
      }
      for (let j = 0; j < extendedStages[i + 1].paths.length; j += 1) {
        futureStage.targets.push(`card-${i + 1}-${[j]}`);
      }
      newFutureStages.push(futureStage);
    }
    newFutureStages[0].sources = newFutureStages[0].sources.filter(
      (s) => s === lastDoor
    );
    setFutureStages(newFutureStages);
  }, [sessionMetadata, currentStage]);

  const handleResize = ({ width }: { width: number }) => {
    setContainerWidth(width);
  };

  return (
    <ResizeObserver onResize={handleResize}>
      <Flex flexDirection="column" position="relative">
        <Connections
          links={links}
          futureStages={futureStages}
          width={containerWidth}
        />
        <Text fontSize="lg" pb={20}>
          {sessionMetadata.lore}
        </Text>
        {sessionMetadata.stages
          .concat(sessionMetadata.stages)
          .concat(sessionMetadata.stages)
          .map((stage, idx) => {
            return (
              <Center key={idx}>
                <StagePanel
                  stageMetadata={stage}
                  onDrop={onDrop}
                  id={idx}
                ></StagePanel>
              </Center>
            );
          })}
      </Flex>
    </ResizeObserver>
  );
};

export default SessionPanel;
