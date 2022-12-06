import React from "react";
import { useQuery } from "react-query";
import { getLayout } from "moonstream-components/src/layoutsForPlay/EngineLayout";
import {
  Box,
  Heading,
  Flex,
  HStack,
  Image,
  Accordion,
  AccordionButton,
  AccordionItem,
  AccordionIcon,
  AccordionPanel,
} from "@chakra-ui/react";
import http from "moonstream-components/src/core/utils/http";
import queryCacheProps from "moonstream-components/src/core/hooks/hookCommon";
import { SHADOWCORN_CONTRACT_ADDRESS } from "moonstream-components/src/core/cu/constants";

const playAssetPath = "https://s3.amazonaws.com/static.simiotics.com/play";
const assets = {
  shadowcornsLogo: `${playAssetPath}/cu/shadowcorns-logo.png`,
};

const buildOpenseaLink = (tokenId: string) => {
  return `https://opensea.io/assets/matic/${SHADOWCORN_CONTRACT_ADDRESS}/${tokenId}`;
};

const Leaderboard = () => {
  const [limit] = React.useState<number>(0);
  const [offset, setOffset] = React.useState<number>(0);
  const [scores, setScores] = React.useState<number[]>([]);

  const fetchLeaders = async (pageLimit: number, pageOffset: number) => {
    return http(
      {
        method: "GET",
        url: `https://engineapi.moonstream.to/leaderboard/?leaderboard_id=863429ad-ea0d-4cbf-b0f9-6e5c3fc83bb2&limit=${pageLimit}&offset=${pageOffset}`,
      },
      true
    );
  };

  const groups = useQuery(
    ["fetch_leaders", limit, offset],
    () => {
      return fetchLeaders(limit, offset).then((res) => {
        try {
          let groups = new Map<number, { rank: number; records: number[] }>();
          for (const record of res.data) {
            if (groups.has(record.score)) {
              let { records } = groups.get(record.score)!;
              records.push(record);
            } else {
              groups.set(record.score, {
                rank: record.rank,
                records: [record],
              });
            }
          }
          console.log(groups);
          setScores(
            Array.from(new Set(res.data.map((item: any) => item.score)))
          );
          return groups;
        } catch (err) {
          console.log(err);
        }
      });
    },
    {
      ...queryCacheProps,
      onSuccess: () => {},
    }
  );

  const panelBackground = "#2D2D2D";

  return (
    <Box className="Dashboard" py={10} bgColor="#1A1D22">
      <Flex
        mb={10}
        borderRadius="20px"
        bgColor={panelBackground}
        px={10}
        py={10}
        direction="column"
      >
        <HStack mb={10}>
          <Image
            ml={2}
            alt={"Shadowcorns"}
            h="50px"
            src={assets["shadowcornsLogo"]}
          />
          <Heading>Throwing Shade Leaderboard</Heading>
        </HStack>
        <Accordion allowToggle>
          {groups.data &&
            groups.data.keys().map((group: any) => {
              return (
                <AccordionItem key={group.score}>
                  <AccordionButton>
                    <Box flex="1" textAlign="left">
                      {item}
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                  <AccordionPanel pb={4}>
                    {leaders.data &&
                      leaders.data.data
                        .filter((record: any) => record.score === item)
                        .map((item: any) => {
                          return (
                            <Flex key={item.address}>
                              {item.rank}
                              {item.address}
                              {item.score}
                            </Flex>
                          );
                        })}
                  </AccordionPanel>
                </AccordionItem>
              );
            })}
        </Accordion>
      </Flex>
    </Box>
  );
};

Leaderboard.getLayout = getLayout;

export default Leaderboard;
