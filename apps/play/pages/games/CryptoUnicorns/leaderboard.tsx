import React, { useContext, useEffect } from "react";
import { useQuery } from "react-query";
import { getLayout } from "moonstream-components/src/layoutsForPlay/EngineLayout";
import {
  Box,
  Heading,
  Flex,
  Image,
  Accordion,
  AccordionButton,
  AccordionItem,
  AccordionPanel,
  AccordionIcon,
  Spacer,
  Link,
  Spinner,
  Grid,
  GridItem,
  Icon,
  HStack,
} from "@chakra-ui/react";
import { InfoOutlineIcon } from "@chakra-ui/icons";
import { FiExternalLink } from "react-icons/fi";

import http from "moonstream-components/src/core/utils/http";
import queryCacheProps from "moonstream-components/src/core/hooks/hookCommon";

import Web3 from "web3";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
const GardenABI = require("../../../games/GoFPABI.json");
import { GOFPFacet as GardenABIType } from "../../../../../types/contracts/GOFPFacet";
const MulticallABI = require("../../../games/cu/Multicall2.json");
import { Multicall2 } from "../../../games/cu/Multicall2";
const ERC721MetadataABI = require("../../../../../abi/MockERC721.json");
import { MockERC721 } from "../../../../../types/contracts/MockERC721";
import { GOFP_CONTRACT_ADDRESS, MULTICALL2_CONTRACT_ADDRESS, SHADOWCORN_CONTRACT_ADDRESS } from "moonstream-components/src/core/cu/constants";
import { EmitHelper, tokenToString } from "typescript";


const playAssetPath = "https://s3.amazonaws.com/static.simiotics.com/play";
const assets = {
  shadowcornsLogo: `${playAssetPath}/cu/shadowcorns-logo.png`,
};

const buildOpenseaLink = (tokenId: string) => {
  return `https://opensea.io/assets/matic/${SHADOWCORN_CONTRACT_ADDRESS}/${tokenId}`;
};

const Leaderboard = () => {
  const [limit] = React.useState<number>(0);
  const [offset] = React.useState<number>(0);
  const [currentAccount, setCurrentAccount] = React.useState(
    GOFP_CONTRACT_ADDRESS
  );

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

  const web3ctx = useContext(Web3Context);

  const convertMulticallResponseAddress = (address: string) => {
    return Web3.utils.toChecksumAddress(address.substring(0, 2) + address.substring(26))
  };

  const allShadowcorns = [ ...Array(2400).keys() ].map(x => (x+1).toString());

  // const fetchExplicitOwners = async () => {
  //   let ownerOfQueries = allShadowcorns.map((tokenId: string) => {
  //     return { target: SHADOWCORN_CONTRACT_ADDRESS, 
  //              callData: shadowcornsContract.methods.ownerOf(tokenId).encodeABI()};
  //   });
  //   return multicallContract.methods.tryAggregate(false, ownerOfQueries).call().then((res: any[]) => {
  //     return res.map((item: any, index: number) => { return { tokenId: (index + 1).toString(), ownerAddress: convertMulticallResponseAddress(item.returnData) } });
  //   });
  // };

  // useEffect(() => {
  //   if (Web3.utils.isAddress(web3ctx.account)) {
  //     setCurrentAccount(web3ctx.account);
  //   }
  // }, [web3ctx.account]);

  const stakedShadowcorns = useQuery(
    ["staked_tokens", currentAccount],
    async () => {
      if(!currentAccount) return;
      const gardenContract = new web3ctx.polygonClient.eth.Contract(
        GardenABI, GOFP_CONTRACT_ADDRESS
      ) as any as GardenABIType;
      const multicallContract = new web3ctx.polygonClient.eth.Contract(
        MulticallABI, MULTICALL2_CONTRACT_ADDRESS
      )
      const numStaked = await gardenContract.methods.numTokensStakedIntoSession(4, currentAccount).call();
      console.log("Num staked: ", numStaked);

      let stakedTokensQueries = [];
      for (var i = 1; i <= parseInt(numStaked); i++) {
        stakedTokensQueries.push({
          target: GOFP_CONTRACT_ADDRESS,
          callData: gardenContract.methods.tokenOfStakerInSessionByIndex(4, currentAccount, i.toString()).encodeABI()
        });
      }

      console.log(stakedTokensQueries);
      return multicallContract.methods.tryAggregate(false, stakedTokensQueries).call().then((res: any[]) => {
        console.log("Staked multicall response");
        console.log(res);
      });

    },
    {
      ...queryCacheProps,
      onSuccess: () => {},
    }
  );

  const ownedShadowcorns = useQuery(
    ["owned_tokens", currentAccount],
    async () => {
      if(!currentAccount) return;
      const shadowcornsContract = new web3ctx.web3.eth.Contract(
        ERC721MetadataABI, SHADOWCORN_CONTRACT_ADDRESS
      ) as unknown as MockERC721;
      const multicallContract = new web3ctx.polygonClient.eth.Contract(
        MulticallABI, MULTICALL2_CONTRACT_ADDRESS
      )
      const numTokens = await shadowcornsContract.methods.balanceOf(currentAccount).call();
      console.log("Num owned: ", numTokens);
      let tokenOfOwnerQueries = [];
      for (var i = 1; i <= parseInt(numTokens); i++) {
        tokenOfOwnerQueries.push({
          target: GOFP_CONTRACT_ADDRESS,
          callData: shadowcornsContract.methods.tokenOfOwnerByIndex(currentAccount, i).encodeABI()
        });
      }
    
      console.log("queries");
      console.log(tokenOfOwnerQueries);
      return multicallContract.methods.tryAggregate(false, tokenOfOwnerQueries).call().then((res: any[]) => {
        console.log("Owned multicall response");
        console.log(res);
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
          Shadowcorns rank on the leaderboard by earning Leaderboard Points.
          Each room a Shadowcorn reaches earns them points. At the end of the
          Throwing Shade Event, the Players will be airdropped rewards based on
          where they rank on the Leaderboard.
        </Box>
        <Grid
          borderBottom="1px solid #8B8B8B"
          templateColumns="1fr 2fr 1fr"
          fontWeight="700"
          pb="10px"
        >
          <GridItem pl={["2px", "5px", "10px"]}>Rank</GridItem>
          <GridItem>Shadowcorn</GridItem>
          <GridItem>Score</GridItem>
        </Grid>
        {groups.data ? (
          <Accordion allowToggle allowMultiple>
            {[...groups.data.entries()].map(([score, group]) => {
              return (
                <AccordionItem
                  borderStyle="none"
                  key={score}
                  fontSize={["xs", "sm", "lg"]}
                >
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
                      <GridItem fontWeight="400">{`${
                        group.records.length
                      } Shadowcorn${
                        group.records.length > 1 ? "s" : ""
                      }`}</GridItem>
                      <GridItem fontWeight="400">
                        <Flex width="100%" justifyContent="space-between">
                          {score}
                          <AccordionIcon />
                        </Flex>
                      </GridItem>
                    </Grid>
                  </AccordionButton>
                  <AccordionPanel p="0px">
                    {group.records.map((item: any) => {
                      return (
                        <Grid
                          key={item.address}
                          textAlign="left"
                          width="100%"
                          templateColumns="1fr 2fr 1fr"
                          py={["5px", "10px"]}
                          bg="#232323"
                        >
                          <GridItem
                            fontWeight="700"
                            pl={["8px", "20px", "40px"]}
                          >
                            {group.rank}
                          </GridItem>

                          <Link
                            p="0px"
                            _hover={{ bgColor: "#454545" }}
                            href={buildOpenseaLink(item.address)}
                            isExternal
                          >
                            <GridItem fontWeight="400">
                              {item.address}
                              <Icon as={FiExternalLink} ml="10px" />
                            </GridItem>
                          </Link>
                          <GridItem fontWeight="400">{item.score}</GridItem>
                        </Grid>
                      );
                    })}
                  </AccordionPanel>
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

Leaderboard.getLayout = getLayout;

export default Leaderboard;
