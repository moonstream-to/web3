import {
  AccordionButton,
  AccordionIcon,
  GridItem,
  Flex,
  Text,
  Spacer,
} from "@chakra-ui/react";
import LeaderboardRank from "./LeaderboardRank";

import GroupImage from "./GroupImage";

const LeaderboardGroupHeader = ({ group, metadata }) => {
  return (
    <AccordionButton _hover={{ bg: "#454545" }} p="0" borderRadius="10px">
      <Flex
        textAlign="left"
        width="100%"
        py={["5px", "5px", "10px"]}
        alignItems="center"
        fontSize={["12px", "12px", "20px"]}
        justifyContent="space-between"
      >
        <GridItem
          maxW={["45px", "45px", "125px"]}
          minW={["45px", "45px", "125px"]}
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
              pl={["0px", "0px", "7px"]}
            >{`${group.records.length} Shadowcorns`}</Text>
          </Flex>
          <Spacer />
        </GridItem>
        <GridItem
          fontWeight="400"
          maxW={["50px", "50px", "140px", "200px"]}
          minW={["50px", "50px", "140px", "200px"]}
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
