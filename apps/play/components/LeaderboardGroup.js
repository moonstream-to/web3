import { AccordionPanel, GridItem, Grid, Link, Icon } from "@chakra-ui/react";
import { FiExternalLink } from "react-icons/fi";
import { SHADOWCORN_CONTRACT_ADDRESS } from "moonstream-components/src/core/cu/constants";

const buildOpenseaLink = (tokenId) => {
  return `https://opensea.io/assets/matic/${SHADOWCORN_CONTRACT_ADDRESS}/${tokenId}`;
};

const LeaderboardGroup = ({ group }) => {
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

            <Link
              p="0px"
              _hover={{ bgColor: "#454545" }}
              href={buildOpenseaLink(item.address)}
              isExternal
            >
              <GridItem fontWeight="400">
                {item.name}
                <Icon as={FiExternalLink} ml="10px" />
              </GridItem>
            </Link>
            <GridItem fontWeight="400">{item.score}</GridItem>
          </Grid>
        );
      })}
    </AccordionPanel>
  );
};

export default LeaderboardGroup;
