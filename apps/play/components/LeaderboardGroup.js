import { AccordionPanel, GridItem, Flex } from "@chakra-ui/react";
import ShadowcornRow from "./ShadocornRow";
import LeaderboardRank from "./LeaderboardRank";

const LeaderboardGroup = ({ group, shadowcorns }) => {
  return (
    <AccordionPanel p="0px">
      <Flex direction="column" borderRadius="10px" bg="#1A1D22">
        {group.records.map((item) => {
          return (
            <Flex
              key={item.address}
              textAlign="left"
              width="100%"
              py={["5px", "5px", "10px"]}
              alignItems="center"
              justifyContent="space-between"
            >
              <GridItem
                maxW={["45px", "45px", "125px"]}
                minW={["45px", "45px", "125px"]}
                pl={["5px", "5px", "20px"]}
              >
                <LeaderboardRank rank={group.rank} />
              </GridItem>
              <GridItem fontWeight="400" mr="auto">
                <ShadowcornRow
                  shadowcorn={shadowcorns.data?.get(item.address)}
                  tokenId={item.address}
                />
              </GridItem>
              <GridItem
                fontWeight="400"
                maxW={["50px", "50px", "140px", "200px"]}
                minW={["50px", "50px", "140px", "200px"]}
              >
                {item.score}
              </GridItem>
            </Flex>
          );
        })}
      </Flex>
    </AccordionPanel>
  );
};

export default LeaderboardGroup;
