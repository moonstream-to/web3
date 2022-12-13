import {
  AccordionButton,
  AccordionIcon,
  GridItem,
  Flex,
  Text,
} from "@chakra-ui/react";
import LeaderboardRank from "./LeaderboardRank";

import GroupImage from "./GroupImage";

const LeaderboardGroupHeader = ({ group, metadata }) => {
  return (
    <AccordionButton _hover={{ bg: "#454545" }} p="0">
      <Flex
        textAlign="left"
        width="100%"
        py={["5px", "5px", "10px"]}
        alignItems="center"
        fontSize={["12px", "16px", "20px"]}
        justifyContent="space-between"
      >
        <GridItem
          maxW={["55px", "55px", "125px"]}
          minW={["55px", "55px", "125px"]}
        >
          <LeaderboardRank rank={group.rank} />
        </GridItem>
        <GridItem fontWeight="400" w="100%">
          <Flex mr="auto" justifyContent="start" alignItems="center">
            <GroupImage
              shadowcorns={
                group.records.length > 2
                  ? group.records.slice(0, 3)
                  : group.records
              }
              metadata={metadata}
            />
            <Text
              pl={["2px", "5px", "7px"]}
            >{`${group.records.length} Shadowcorns`}</Text>
          </Flex>
        </GridItem>
        <GridItem
          fontWeight="400"
          maxW={["60px", "80px", "240px"]}
          minW={["60px", "80px", "240px"]}
        >
          <Flex justifyContent="space-between">
            {group.score}
            <AccordionIcon />
          </Flex>
        </GridItem>
      </Flex>
    </AccordionButton>
  );
};

export default LeaderboardGroupHeader;
