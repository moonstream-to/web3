import {
  AccordionButton,
  AccordionIcon,
  Grid,
  GridItem,
  Flex,
} from "@chakra-ui/react";

const LeaderboardGroupHeader = ({ group }) => {
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
        <GridItem fontWeight="400">{`${group.records.length} Shadowcorn${
          group.records.length > 1 ? "s" : ""
        }`}</GridItem>
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
