import React, { useState } from "react";
import { Flex, Text } from "@chakra-ui/react";
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
  const [links, setLinks] = useState(new Map<string, string[]>());
  const handleResize = () => {
    const newLinks = new Map<string, string[]>();
    newLinks.set("card-0-1", ["card-1-0"]);
    newLinks.set("card-1-0", ["card-2-3"]);
    newLinks.set("card-2-3", ["card-3-1"]);
    newLinks.set("card-3-1", ["card-4-1"]);
    newLinks.set("card-4-1", ["card-5-1", "card-5-0", "card-5-2", "card-5-3"]);
    newLinks.set("card-5-1", ["card-6-1", "card-6-0", "card-6-2"]);
    newLinks.set("card-6-2", ["card-7-1", "card-7-0", "card-7-2"]);
    newLinks.set("card-7-0", ["card-8-1", "card-8-0", "card-8-2", "card-8-3"]);

    setLinks(newLinks);
  };

  return (
    <ResizeObserver onResize={handleResize}>
      <Flex flexDirection="column" position="relative">
        <Connections links={links} />
        <Text fontSize="lg" pb={20}>
          {sessionMetadata.lore}
        </Text>
        {sessionMetadata.stages
          .concat(sessionMetadata.stages)
          .concat(sessionMetadata.stages)
          .map((stage, idx) => {
            return (
              <StagePanel
                key={idx}
                stageMetadata={stage}
                onDrop={onDrop}
                id={idx}
              ></StagePanel>
            );
          })}
      </Flex>
    </ResizeObserver>
  );
};

export default SessionPanel;
