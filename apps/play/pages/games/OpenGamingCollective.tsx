import React, { useContext, useEffect } from "react";
import { getLayout } from "moonstream-components/src/layoutsForPlay/EngineLayout";
import {
  Flex,
  Center,
  Spacer,
  Image,
  Box,
  Text,
  Input,
  InputGroup,
  InputRightElement,
  Button,
  Grid,
} from "@chakra-ui/react";

import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
import { useQuery } from "react-query";
import { useRouter } from "moonstream-components/src/core/hooks";
import { DEFAULT_METATAGS } from "../../src/constants";
import LootboxCard from "moonstream-components/src/components/CryptoUnicorns/LootboxCardPlay";
import { MockTerminus as TerminusFacet } from "../../../../types/contracts/MockTerminus";
import { hookCommon } from "moonstream-components/src/core/hooks";

const terminusAbi = require("../../../../abi/MockTerminus.json");

type terminusType = "type1" | "type2" | "type3";

// TODO: Using an Enum here would make this less clumsy. The Enum defines a type *and* a value.
const terminusTypes: terminusType[] = ["type1", "type2", "type3"];

const terminusPoolIds: { [key in terminusType]: number } = {
  type1: 1,
  type2: 2,
  type3: 3,
};

const defaultBalances: { [key in terminusType]: number } = {
  type1: 0,
  type2: 0,
  type3: 0,
};

const OpenGamingCollective = () => {
  const web3ctx = useContext(Web3Context);
  const router = useRouter();
  var defaultSpyAddress = router.query["spyAddress"];
  if (!web3ctx.web3.utils.isAddress(defaultSpyAddress)) {
    defaultSpyAddress = undefined;
  }
  const [currentAccount, setCurrentAccount] = React.useState(
    defaultSpyAddress || "0x0000000000000000000000000000000000000000"
  );
  const terminusAddress = "0xa4BE88fF51D069430E4DdAF6b3044353954cf011";
  const spyAddressInput = React.useRef<HTMLInputElement | null>(null);

  const [spyMode, setSpyMode] = React.useState(!!defaultSpyAddress);

  useEffect(() => {
    if (!spyMode) {
      setCurrentAccount(web3ctx.account);
    }
  }, [web3ctx.account, spyMode]);

  // Fetch terminus balances.
  const terminusBalances = useQuery(
    currentAccount,
    async ({ queryKey }) => {
      const currentUserAddress = queryKey[0];

      if (currentUserAddress == "0x0000000000000000000000000000000000000000") {
        return;
      }

      const terminusFacet = new web3ctx.polygonClient.eth.Contract(
        terminusAbi
      ) as any as TerminusFacet;
      terminusFacet.options.address = terminusAddress;

      let accounts: string[] = [];
      let poolIds: number[] = [];

      terminusTypes.forEach((terminusType) => {
        const pool = terminusPoolIds[terminusType];
        if (pool > 0) {
          accounts.push(`${currentUserAddress}`);
          poolIds.push(pool);
        }
      });

      let currentBalances = { ...defaultBalances };

      try {
        const balances = await terminusFacet.methods
          .balanceOfBatch(accounts, poolIds)
          .call();
        balances.forEach((balance, index) => {
          currentBalances[terminusTypes[index]] = parseInt(balance, 10);
        });
      } catch (e) {
        console.error(
          `Open Gaming Collective Portal: Could not retrieve terminus balances for the given user: ${currentUserAddress}. Terminus pool IDs: ${poolIds}. Terminus contract address: ${terminusAddress}.`
        );
      }

      return currentBalances;
    },
    {
      ...hookCommon,
    }
  );

  const PLAY_ASSET_PATH = "https://s3.amazonaws.com/static.simiotics.com/play";
  const assets = {
    logo: `${PLAY_ASSET_PATH}/ogc/logo.png`,
    blackSpyIcon: `${PLAY_ASSET_PATH}/games/spy-icon-black.png`,
    whiteSpyIcon: `${PLAY_ASSET_PATH}/games/spy-icon-white.png`,
  };

  const badges = [
    {
      imageUrl:
        "https://badges.moonstream.to/open-gaming-collective/open-gaming-gr15-open-source-trumps-all.png",
      displayName: "Gitcoin GR15: Open Source Trumps All",
      balanceKey: "type1",
    },
    {
      imageUrl:
        "https://badges.moonstream.to/open-gaming-collective/gr15-i-demoed.png",
      displayName: "Gitcoin GR15: I Demoed!",
      balanceKey: "type2",
    },
    {
      imageUrl:
        "https://badges.moonstream.to/open-gaming-collective/GR15-OG_Tesseract_final.png",
      displayName: "Gitcoin GR15: The Open Gaming Tesseract",
      balanceKey: "type3",
    },
  ];

  return (
    <Flex
      className="Games"
      borderRadius={"xl"}
      bgColor={spyMode ? "#1A1D22" : "#1A1D22"}
    >
      <Flex w="100%" minH="100vh" direction={"column"} px="7%" mt="50px">
        {spyMode && (
          <Flex
            w="100%"
            direction={"row"}
            h="55px"
            mt={10}
            mb={12}
            pl={6}
            bgColor={spyMode ? "#4A4A4A" : "pink.500"}
            borderRadius={"xl"}
            boxShadow="xl"
            placeItems={"center"}
            fontSize={"lg"}
          >
            <Image
              src={assets["whiteSpyIcon"]}
              alt="Spy Mode"
              h="16px"
              pr="2"
            ></Image>
            Spy Mode
            <Spacer />
            <Center
              display="inline-flex"
              pr={6}
              onClick={() => {
                setSpyMode(false);
                if (spyAddressInput?.current != null) {
                  spyAddressInput.current.value = "";
                }
              }}
            >
              <Text pr={2} cursor="pointer">
                exit
              </Text>
              {/* <CloseIcon h="10px" /> */}
            </Center>
          </Flex>
        )}
        {spyMode && (
          <Flex w="100%" pb={4}>
            <InputGroup size="md" textColor={"white"}>
              <Input
                ref={spyAddressInput}
                colorScheme="transparent"
                bgColor="transparent"
                variant="outline"
                defaultValue={defaultSpyAddress || undefined}
                onChange={(e) => {
                  const nextValue = e.target.value;
                  if (web3ctx.web3.utils.isAddress(nextValue)) {
                    setCurrentAccount(nextValue);
                  }
                }}
                placeholder="Type an address"
                _placeholder={{ color: "white" }}
              />
              <InputRightElement width="3rem">
                <Button
                  h="2rem"
                  size="md"
                  bg="transparent"
                  _hover={{
                    backgroundColor: "transparent",
                  }}
                  _focus={{
                    textDecoration: "none",
                  }}
                  onClick={() => {
                    if (spyAddressInput?.current != null) {
                      spyAddressInput.current.value = "";
                    }
                  }}
                >
                  X
                </Button>
              </InputRightElement>
            </InputGroup>
          </Flex>
        )}
        <Box>
          <Grid templateColumns="repeat(4, 1fr)" gap={6} mb={6}>
            {badges.map((item: any, idx: any) => {
              if (!terminusBalances?.data) {
                return;
              }
              const quantity =
                terminusBalances.data[item["balanceKey"] as terminusType];

              return (
                <LootboxCard
                  key={idx}
                  imageUrl={item["imageUrl"]}
                  displayName={item["displayName"]}
                  lootboxBalance={quantity}
                  showQuantity={false}
                  grayedOut={quantity <= 0}
                />
              );
            })}
          </Grid>
        </Box>
        {!spyMode && (
          <Button
            size="sm"
            height="24px"
            width="150px"
            textColor="#D43F8C"
            borderColor="#FFFFFF"
            bgColor="white"
            borderRadius="md"
            onClick={() => {
              if (defaultSpyAddress) {
                setCurrentAccount(defaultSpyAddress);
              }
              setSpyMode(true);
            }}
            mb={10}
          >
            <Image
              src={assets["blackSpyIcon"]}
              alt="Spy Mode"
              h="16px"
              pr="2"
            ></Image>
            Spy Mode
          </Button>
        )}
      </Flex>
    </Flex>
  );
};

export async function getStaticProps() {
  const metatags = {
    title: "Moonstream community portal: Open Gaming Collective",
    description: "See your Open Gaming Collective badges",
  };
  return {
    props: { metaTags: { DEFAULT_METATAGS, ...metatags } },
  };
}

OpenGamingCollective.getLayout = getLayout;

export default OpenGamingCollective;
