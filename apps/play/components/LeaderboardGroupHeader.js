import {
  AccordionButton,
  AccordionIcon,
  Grid,
  GridItem,
  Flex,
  HStack,
  Text,
} from "@chakra-ui/react";

import GroupImage from "./GroupImage";

const LeaderboardGroupHeader = ({ group, metadata }) => {
  return (
    <AccordionButton
      fontSize={["xs", "sm", "lg"]}
      _hover={{ bg: "#454545" }}
      p="0"
    >
      <Grid
        textAlign="left"
        width="100%"
        templateColumns="1fr 2fr 1fr"
        py={["5px", "10px"]}
      >
        <GridItem fontWeight="700" pl={["4px", "10px", "20px"]}>
          {group.rank}
        </GridItem>
        <GridItem fontWeight="400">
          <HStack align="center">
            <GroupImage
              shadowcorns={
                group.records.length > 2
                  ? group.records.slice(0, 3)
                  : group.records
              }
              metadata={metadata}
            />
            <Text pl="7px">{`${group.records.length} Shadowcorns`}</Text>
          </HStack>
        </GridItem>
        <GridItem fontWeight="400">
          <Flex width="100%" justifyContent="space-between">
            {group.score}
            <AccordionIcon />
          </Flex>
        </GridItem>
      </Grid>
    </AccordionButton>
  );
};

export default LeaderboardGroupHeader;
