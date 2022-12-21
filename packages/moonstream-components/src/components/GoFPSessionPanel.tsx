import React from "react";
import { Flex, Text } from "@chakra-ui/react";
import { SessionMetadata } from "./GoFPTypes";
import StagePanel from "./GoFPStagePanel";

const SessionPanel = ({
  sessionMetadata,
}: {
  sessionMetadata: SessionMetadata;
}) => {
  return (
    <Flex flexDirection="column">
      <Text fontSize="lg" pb={20}>
        {sessionMetadata.lore}
      </Text>
      {sessionMetadata.stages.map((stage, idx) => {
        return <StagePanel key={idx} stageMetadata={stage}></StagePanel>;
      })}
    </Flex>
  );
};

export default SessionPanel;
