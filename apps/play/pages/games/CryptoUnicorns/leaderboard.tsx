import React from "react";
import { useQuery } from "react-query";
import { getLayout } from "moonstream-components/src/layoutsForPlay/EngineLayout";
import LeaderboardGroupHeader from "./../../../components/LeaderboardGroupHeader";
import LeaderboardGroup from "./../../../components/LeaderboardGroup";
import ShadowcornRow from "../../../components/ShadocornRow";
import LeaderboardRank from "./../../../components/LeaderboardRank";
// import LeaderboardRank from "./../../../components/LeaderboardRank";

import {
  Box,
  Heading,
  Flex,
  Image,
  Accordion,
  AccordionItem,
  Spacer,
  Link,
  Spinner,
  GridItem,
  HStack,
} from "@chakra-ui/react";
import { InfoOutlineIcon } from "@chakra-ui/icons";

import http from "moonstream-components/src/core/utils/http";
import queryCacheProps from "moonstream-components/src/core/hooks/hookCommon";
import { DEFAULT_METATAGS } from "../../../src/constants";

const playAssetPath = "https://s3.amazonaws.com/static.simiotics.com/play";
const assets = {
  shadowcornsLogo: `${playAssetPath}/cu/shadowcorns-logo.png`,
};

const Leaderboard = () => {
  const [limit] = React.useState<number>(0);
  const [offset] = React.useState<number>(0);

  const fetchLeaders = async (pageLimit: number, pageOffset: number) => {
    return http(
      {
        method: "GET",
        url: `https://engineapi.moonstream.to/leaderboard/?leaderboard_id=863429ad-ea0d-4cbf-b0f9-6e5c3fc83bb2&limit=${pageLimit}&offset=${pageOffset}`,
      },
      true
    );
  };

  const fetchShadowcorns = async () => {
    return http(
      {
        method: "GET",
        url: "https://data.moonstream.to/shadowcorns/shadowcorns.json",
      },
      true
    );
  };

  const shadowcorns = useQuery(
    ["fetch_shadowcorns"],
    () => {
      return fetchShadowcorns().then((res) => {
        const shadowcorns = new Map<
          string,
          { tokenId: number; name: string; image: string }
        >();
        res.data.forEach(
          (sc: {
            token_id: number;
            metadata: {
              name: string;
              attributes: [{ trait_type: string; value: string }];
            };
          }) => {
            const { name, attributes } = sc.metadata;
            const image = `${playAssetPath}/cu/shadowcorns/shadowcorn_${
              attributes
                .find((attr) => attr.trait_type === "Class")
                ?.value.toLowerCase() ?? ""
            }_${
              attributes
                .find((attr) => attr.trait_type === "Rarity")
                ?.value.toLowerCase() ?? ""
            }.jpg`;
            shadowcorns.set(String(sc.token_id), {
              tokenId: sc.token_id,
              name,
              image,
            });
          }
        );
        return shadowcorns;
      });
    },
    {
      ...queryCacheProps,
      onSuccess: () => {},
    }
  );

  const groups = useQuery(
    ["fetch_leaders", limit, offset],
    () => {
      return fetchLeaders(limit, offset).then((res) => {
        try {
          let groups = new Map<
            number,
            {
              rank: number;
              records: { address: string; rank: number; score: number }[];
              score: number;
            }
          >();
          for (const record of res.data) {
            if (groups.has(record.score)) {
              let { records } = groups.get(record.score)!;
              records.push(record);
            } else {
              groups.set(record.score, {
                rank: record.rank,
                records: [record],
                score: record.score,
              });
            }
          }
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
    <Box
      className="Dashboard"
      py={["10px", "20px", "30px"]}
      bgColor="#1A1D22"
      maxW="1200px"
    >
      <Flex
        borderRadius="20px"
        bgColor={panelBackground}
        p={[2, 4, 10]}
        direction="column"
        fontSize={["xs", "sm", "lg"]}
      >
        <Flex alignItems="center" direction={["column", "column", "row"]}>
          <HStack>
            <Image
              ml={2}
              alt={"Shadowcorns"}
              h="50px"
              src={assets["shadowcornsLogo"]}
            />
            <Heading fontSize={["lg", "2xl"]}>
              Throwing Shade Leaderboard
            </Heading>
          </HStack>
          <Spacer />
          <Flex
            w={["100%", "100%", "228px"]}
            justifyContent={["start", "start", "end"]}
            mt={["10px", "10px", 0]}
          >
            <Link
              verticalAlign="middle"
              fontSize={["xs", "sm", "lg"]}
              py={["2px", "5px", "10px"]}
              px={["4px", "10px", "20px"]}
              borderRadius="40px"
              href={
                "https://medium.com/@lagunagames/shadowcorns-throwing-shade-4a887d8737bf"
              }
              _hover={{
                bg: "#232323",
                textTransform: "none",
              }}
              isExternal
            >
              <Flex alignItems="center">
                {" "}
                <Box>About the event</Box>
                <InfoOutlineIcon ml={[0.5, 1.25, 2.5]} />
              </Flex>
            </Link>
          </Flex>
        </Flex>
        <Box my={["10px", "20px", "30px"]} fontSize={["xs", "sm", "lg"]}>
          This leaderboard ranks Shadowcorn NFTs and not player wallets. Each
          room a Shadowcorn reaches during the Throwing Shade Event earns them
          points. At the end of the event, players will be airdropped rewards
          according to their Shadowcorns&apos; ranks. Shadowcorns can share
          ranks.
        </Box>
        <Flex
          textAlign="left"
          width="100%"
          justifyContent="space-between"
          py={["5px", "5px", "10px"]}
          alignItems="center"
          borderBottom="1px solid white"
          fontSize={["14px", "18px", "20px"]}
          fontWeight="700"
        >
          <GridItem
            pl={["2px", "5px", "10px"]}
            maxW={["55px", "55px", "125px"]}
            minW={["55px", "55px", "125px"]}
          >
            Rank
          </GridItem>
          <GridItem mr="auto">Shadowcorn</GridItem>
          <GridItem
            maxW={["60px", "80px", "240px"]}
            minW={["60px", "80px", "240px"]}
          >
            Score
          </GridItem>
        </Flex>
        {groups.data ? (
          <Accordion
            allowToggle
            allowMultiple
            fontSize={["12px", "16px", "20px"]}
          >
            {[...groups.data.entries()].map(([score, group]) => {
              return (
                <AccordionItem
                  borderStyle="none"
                  key={score}
                  verticalAlign="center"
                >
                  {group.records.length > 1 && (
                    <>
                      <LeaderboardGroupHeader
                        metadata={shadowcorns.data}
                        group={group}
                      />
                      <LeaderboardGroup
                        group={group}
                        shadowcorns={shadowcorns}
                      />
                    </>
                  )}
                  {group.records.length === 1 && (
                    <Flex
                      textAlign="left"
                      width="100%"
                      justifyContent="space-between"
                      py={["5px", "5px", "10px"]}
                      alignItems="center"
                    >
                      <GridItem
                        maxW={["55px", "55px", "125px"]}
                        minW={["55px", "55px", "125px"]}
                      >
                        <LeaderboardRank rank={group.rank} />
                      </GridItem>
                      <GridItem fontWeight="400" mr="auto">
                        <ShadowcornRow
                          shadowcorn={shadowcorns.data?.get(
                            group.records[0].address
                          )}
                          tokenId={group.records[0].address}
                        />
                      </GridItem>
                      <GridItem
                        my="auto"
                        fontWeight="400"
                        maxW={["60px", "80px", "240px"]}
                        minW={["60px", "80px", "240px"]}
                      >
                        <Flex width="100%" justifyContent="space-between">
                          {group.score}
                        </Flex>
                      </GridItem>
                    </Flex>
                  )}
                </AccordionItem>
              );
            })}
          </Accordion>
        ) : (
          <Spinner alignSelf="center" />
        )}
      </Flex>
    </Box>
  );
};

export async function getStaticProps() {
  const metatags = {
    title: "Moonstream player portal: Throwing Shade",
    description: "Throwing Shade Leaderboard",
  };
  return {
    props: { metaTags: { DEFAULT_METATAGS, ...metatags } },
  };
}

Leaderboard.getLayout = getLayout;
export default Leaderboard;
