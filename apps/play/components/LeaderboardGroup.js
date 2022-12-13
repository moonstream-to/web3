import { AccordionPanel, GridItem, Grid } from "@chakra-ui/react";
import ShadowcornRow from "./ShadocornRow";

const LeaderboardGroup = ({ group, shadowcorns }) => {
  return (
    <AccordionPanel p="0px">
      {group.records.map((item) => {
        return (
          <Grid
            key={item.address}
            textAlign="left"
            width="100%"
            templateColumns="1fr 2fr 1fr"
            py={["5px", "10px"]}
            bg="#232323"
          >
            <GridItem fontWeight="700" pl={["8px", "20px", "40px"]}>
              {group.rank}
            </GridItem>

            <GridItem fontWeight="400">
              <ShadowcornRow
                shadowcorn={shadowcorns.data?.get(item.address)}
                tokenId={item.address}
              />
            </GridItem>
            <GridItem fontWeight="400">{item.score}</GridItem>
          </Grid>
        );
      })}
    </AccordionPanel>
  );
};

export default LeaderboardGroup;
