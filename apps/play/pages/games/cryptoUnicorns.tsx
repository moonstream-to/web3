import React, { useContext, useEffect } from "react";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
import {
  Flex,
  Center,
  Badge,
  Spacer,
  Image,
  Spinner,
  Box,
  Text,
  Stack,
  Input,
  InputGroup,
  FormLabel,
  FormControl,
  FormErrorMessage,
  Button,
  HStack,
  Grid,
  GridItem,
} from "@chakra-ui/react";
const StashABI = require("../../games/cu/StashABI.json");
import { StashABI as StashABIType } from "../../games/cu/StashABI";
const GameBankABI = require("../../games/cu/GameBankABI.json");
import { GameBankABI as GameBankABIType } from "../../games/cu/GameBankABI";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
import { supportedChains } from "../../../../types/Moonstream";
import { useERC20, useToast } from "moonstream-components/src/core/hooks";
import { useMutation, useQuery } from "react-query";
import { DEFAULT_METATAGS } from "../../src/constants";
import {
  MAX_INT,
  chainByChainId,
} from "moonstream-components/src/core/providers/Web3Provider";
import LootboxCard from "../../../../packages/moonstream-components/src/components/CryptoUnicorns/LootboxCard";
import { MockTerminus as TerminusFacet } from "../../../../types/contracts/MockTerminus";
import { hookCommon } from "moonstream-components/src/core/hooks";

const terminusAbi = require("../../../../abi/MockTerminus.json");

const GameBankAddresses: { [key in supportedChains]: string } = {
  mumbai: "0x762aF8cbE298bbFE568BBB6709f854A01c07333D",
  polygon: "0x94f557dDdb245b11d031F57BA7F2C4f28C4A203e",
  ethereum: "0x0000000000000000000000000000000000000000",
  localhost: "0x0000000000000000000000000000000000000000",
};

const TerminusAddresses: { [key in supportedChains]: string } = {
  mumbai: "0x19e812EdB24B68A8F3AbF5e4C82d10AfEf1641Db",
  polygon: "0x99A558BDBdE247C2B2716f0D4cFb0E246DFB697D",
  ethereum: "0x0000000000000000000000000000000000000000",
  localhost: "0x0000000000000000000000000000000000000000",
};

const UNIMAddresses: { [key in supportedChains]: string } = {
  mumbai: "0x47d0f0BD94188e3f8c6fF2C0B1Bf7D6D8BED7534",
  polygon: "0x64060aB139Feaae7f06Ca4E63189D86aDEb51691",
  ethereum: "0x0000000000000000000000000000000000000000",
  localhost: "0x0000000000000000000000000000000000000000",
};

const RBWAddresses: { [key in supportedChains]: string } = {
  mumbai: "0x4Df452487E6c9d0C3Dc5EB4936244F8572b3F0b6",
  polygon: "0x431CD3C9AC9Fc73644BF68bF5691f4B83F9E104f",
  ethereum: "0x0000000000000000000000000000000000000000",
  localhost: "0x0000000000000000000000000000000000000000",
};

type LootboxType = "common" | "rare" | "mythic" | "land" | "mystery" | "RMP";
interface LootboxInfo {
  poolIdByChain: {
    [key in supportedChains]: number;
  };
}

// TODO: Using an Enum here would make this less clumsy. The Enum defines a type *and* a value.
const lootboxTypes: LootboxType[] = [
  "common",
  "rare",
  "mythic",
  "land",
  "mystery",
  "RMP",
];

// TODO(kellan): Rename to "terminusInfo". Map other relevant Terminus pools, such as Golden Tickets (pool ID 42 on mainnet),
// Shadowcorn Act I badges (pool IDs 43, 44, 45 on mainnet), etc.
// To get the balances, we should use multicall: https://www.npmjs.com/package/ethereum-multicall
// You will probably also want to rename "lootboxTypes" above to "terminusTypes". Maybe rename the lootbox keys to contain the string "Lootbox" at the end.
// So "common" -> "commonLootbox".
const lootboxInfo: { [key in LootboxType]: LootboxInfo } = {
  common: {
    poolIdByChain: {
      mumbai: 6,
      polygon: 4,
      ethereum: -1,
      localhost: -1,
    },
  },
  rare: {
    poolIdByChain: {
      mumbai: 7,
      polygon: -1,
      ethereum: -1,
      localhost: -1,
    },
  },
  mythic: {
    poolIdByChain: {
      mumbai: 8,
      polygon: -1,
      ethereum: -1,
      localhost: -1,
    },
  },
  mystery: {
    poolIdByChain: {
      mumbai: 11,
      polygon: -1,
      ethereum: -1,
      localhost: -1,
    },
  },
  RMP: {
    poolIdByChain: {
      mumbai: 12,
      polygon: -1,
      ethereum: -1,
      localhost: -1,
    },
  },
  land: {
    poolIdByChain: {
      mumbai: 26,
      polygon: -1,
      ethereum: -1,
      localhost: -1,
    },
  },
};

const defaultLootboxBalances = {
  common: 0,
  rare: 0,
  mythic: 0,
  land: 0,
  mystery: 0,
  RMP: 0,
};

const CryptoUnicorns = () => {
  const [notEnoughRBW, setNotEnoughRBW] = React.useState(false);
  const [notEnoughUNIM, setNotEnoughUNIM] = React.useState(false);
  const [needAllowanceRBW, setNeedAllowanceRBW] = React.useState(false);
  const [needAllowanceUNIM, setNeedAllowanceUNIM] = React.useState(false);
  const [rbwToStash, setRBWToStash] = React.useState("");
  const [unimToStash, setUNIMToStash] = React.useState("");
  const [terminusAddress, setTerminusAddress] = React.useState("");
  const [UNIMAddress, setUNIMAddress] = React.useState("");
  const [RBWAddress, setRBWAddress] = React.useState("");
  const [gameBankAddress, setGameBankAddress] = React.useState("");
  // TODO(kellan): Remove getGameBankConfig and replace with the same pair of:
  // - useEffect to store addresses when the chain changes
  // - useQuery (with enabled: false) + additional useEffect to retrieve balances when contract address, chain, and other dependencies (like the user address in spy mode) change
  const [UNIMBalance, setUNIMBalance] = React.useState("0");
  const [RBWBalance, setRBWBalance] = React.useState("0");
  const [lootboxBalances, setLootboxBalances] = React.useState({
    ...defaultLootboxBalances,
  });
  // TODO(kellan): Currently, we use web3ctx.account as the address for which to retrieve inventory. This
  // assumption was fine when we only had stash functionality on this page because that account would have
  // to sign transactions.
  // For spy mode, it would be a good idea to have a separate state variable like "currentAccount" which
  // users could set through a spy mode form field if they wanted to.

  const web3ctx = useContext(Web3Context);

  useEffect(() => {
    const chain: string | undefined = chainByChainId[web3ctx.chainId];
    if (!chain) {
      setTerminusAddress("");
      setUNIMAddress("");
      setRBWAddress("");
      setGameBankAddress("");
    } else {
      setTerminusAddress(TerminusAddresses[chain as supportedChains]);
      setUNIMAddress(UNIMAddresses[chain as supportedChains]);
      setRBWAddress(RBWAddresses[chain as supportedChains]);
      setGameBankAddress(GameBankAddresses[chain as supportedChains]);
    }
  }, [web3ctx.chainId]);

  const terminusBalances = useQuery(
    ["cuTerminus", web3ctx.chainId, terminusAddress, web3ctx.account],
    async ({ queryKey }) => {
      const currentChain = chainByChainId[queryKey[1] as number];
      const currentUserAddress = queryKey[3];
      if (!currentChain) {
        return;
      }
      const terminusFacet = new web3ctx.web3.eth.Contract(
        terminusAbi
      ) as any as TerminusFacet;
      terminusFacet.options.address = terminusAddress;

      let accounts: string[] = [];
      let poolIds: number[] = [];

      lootboxTypes.forEach((lootboxType) => {
        accounts.push(`${currentUserAddress}`);
        poolIds.push(
          lootboxInfo[lootboxType].poolIdByChain[
            currentChain as supportedChains
          ]
        );
      });

      try {
        const balances = await terminusFacet.methods
          .balanceOfBatch(accounts, poolIds)
          .call();
        let currentBalances = { ...defaultLootboxBalances };
        balances.forEach((balance, lootboxIndex) => {
          currentBalances[lootboxTypes[lootboxIndex]] = parseInt(balance, 10);
        });
        setLootboxBalances(currentBalances);
      } catch (e) {
        console.error(
          `Crypto Unicorns player portal: Could not retrieve lootbox balances for the given user: ${currentUserAddress}. Lootbox pool IDs: ${poolIds}. Terminus contract address: ${terminusAddress}.`
        );
      }
    },
    {
      ...hookCommon,
      enabled: false,
    }
  );

  useEffect(() => {
    terminusBalances.refetch();
  }, [terminusBalances, web3ctx]);

  const getGameBankConfig = async () => {
    if (!web3ctx.web3.currentProvider) {
      return {
        rbwAddress: "0x0000000000000000000000000000000000000000",
        unimAddress: "0x0000000000000000000000000000000000000000",
        gameServer: "0x0000000000000000000000000000000000000000",
        terminusAddress: "0x0000000000000000000000000000000000000000",
      };
    }
    const contract = new web3ctx.web3.eth.Contract(
      StashABI
    ) as any as StashABIType;

    const gameBankContract = new web3ctx.web3.eth.Contract(
      GameBankABI
    ) as unknown as GameBankABIType;

    contract.options.address =
      GameBankAddresses[
        web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
      ];
    const rbwAddress = await contract.methods.getRBWAddress().call();
    const unimAddress = await contract.methods.getUNIMAddress().call();
    const gameServer = await contract.methods.getGameServer().call();
    const terminusAddress = await gameBankContract.methods
      .getTerminusTokenAddress()
      .call();
    return { rbwAddress, unimAddress, gameServer, terminusAddress };
  };

  const stashContract = useQuery(
    [
      "stashContract",
      GameBankAddresses[
        web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
      ],
    ],
    getGameBankConfig
  );

  const rbw = useERC20({
    contractAddress: stashContract.data?.rbwAddress,
    ctx: web3ctx,
    spender:
      GameBankAddresses[
        web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
      ],
  });
  const unim = useERC20({
    contractAddress: stashContract.data?.unimAddress,
    spender:
      GameBankAddresses[
        web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
      ],
    ctx: web3ctx,
  });
  const contract = new web3ctx.web3.eth.Contract(
    StashABI
  ) as any as StashABIType;

  contract.options.address =
    GameBankAddresses[
      web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
    ];

  const playAssetPath = "https://s3.amazonaws.com/static.simiotics.com/play";
  const assets = {
    unicornMilk: `${playAssetPath}/CU_UNIM_256px.png`,
  };

  const toast = useToast();
  const stashUnim = useMutation(
    (amount: string) =>
      contract.methods.stashUNIM(web3ctx.web3.utils.toWei(amount)).send({
        from: web3ctx.account,
        gasPrice:
          process.env.NODE_ENV !== "production" ? "100000000000" : undefined,
      }),
    {
      onSuccess: () => {
        toast("Transaction went to the moon!", "success");
      },
      onError: () => {
        toast("Transaction failed >.<", "error");
      },
    }
  );

  const stashRBW = useMutation(
    (amount: string) =>
      contract.methods.stashRBW(web3ctx.web3.utils.toWei(amount)).send({
        from: web3ctx.account,
        gasPrice:
          process.env.NODE_ENV !== "production" ? "100000000000" : undefined,
      }),
    {
      onSuccess: () => {
        toast("Transaction went to the moon!", "success");
      },
      onError: () => {
        toast("Transaction failed >.<", "error");
      },
    }
  );

  React.useLayoutEffect(() => {
    if (unim.spenderState.data?.allowance && unimToStash.length !== 0) {
      if (
        web3ctx.web3.utils
          .toBN(unim.spenderState.data.allowance)
          .cmp(
            web3ctx.web3.utils.toBN(
              web3ctx.web3.utils.toWei(unimToStash, "ether")
            )
          ) == -1
      ) {
        setNeedAllowanceUNIM(true);
      } else {
        setNeedAllowanceUNIM(false);
      }
    } else {
      setNeedAllowanceUNIM(false);
    }
    if (unim.spenderState.data?.balance && unimToStash.length !== 0) {
      if (
        web3ctx.web3.utils
          .toBN(unim.spenderState.data.balance)
          .cmp(
            web3ctx.web3.utils.toBN(
              web3ctx.web3.utils.toWei(unimToStash, "ether")
            )
          ) == -1
      ) {
        setNotEnoughUNIM(true);
      } else {
        setNotEnoughUNIM(false);
      }
    } else {
      setNotEnoughUNIM(false);
    }
  }, [unimToStash, unim.spenderState.data, web3ctx.web3.utils]);

  React.useLayoutEffect(() => {
    if (rbw.spenderState.data?.allowance && rbwToStash.length !== 0) {
      if (
        web3ctx.web3.utils
          .toBN(rbw.spenderState.data.allowance)
          .cmp(
            web3ctx.web3.utils.toBN(
              web3ctx.web3.utils.toWei(rbwToStash, "ether")
            )
          ) == -1
      ) {
        setNeedAllowanceRBW(true);
      } else {
        setNeedAllowanceRBW(false);
      }
    } else {
      setNeedAllowanceRBW(false);
    }
    if (rbw.spenderState.data?.balance && rbwToStash.length !== 0) {
      if (
        web3ctx.web3.utils
          .toBN(rbw.spenderState.data.balance)
          .cmp(
            web3ctx.web3.utils.toBN(
              web3ctx.web3.utils.toWei(rbwToStash, "ether")
            )
          ) == -1
      ) {
        setNotEnoughRBW(true);
      } else {
        setNotEnoughRBW(false);
      }
    } else {
      setNotEnoughRBW(false);
    }
  }, [rbwToStash, rbw.spenderState.data, web3ctx.web3.utils]);

  const handleSubmit = () => {};

  const handleKeypress = (e: any) => {
    //it triggers by pressing the enter key
    if (e.charCode === 13) {
      handleSubmit();
    }
  };

  if (
    contract.options.address === "0x0000000000000000000000000000000000000000"
  ) {
    return (
      <Flex
        w="300px"
        h="220px"
        placeSelf={"center"}
        alignSelf="center"
        fontSize={"20px"}
      >
        There is contract on this chain
      </Flex>
    );
  }

  return (
    <Flex className="Games" borderRadius={"xl"} bgColor={"blue.1000"}>
      <Flex w="100%" minH="100vh" direction={"column"} px="7%" mt="100px">
        <Flex
          w="100%"
          direction={"row"}
          flexWrap="wrap"
          mb={12}
          bgColor="pink.500"
          borderRadius={"xl"}
          boxShadow="xl"
          placeItems={"center"}
        >
          <Flex direction={"column"}>
            <Badge
              colorScheme={"pink"}
              variant={"solid"}
              fontSize={"md"}
              borderRadius={"md"}
              mr={2}
              p={1}
            >
              <HStack>
                <Image
                  ml={2}
                  alt={"bottle"}
                  h="48px"
                  src={assets["unicornMilk"]}
                />
                <Flex direction={"column"} wrap="nowrap" w="100%">
                  <code>
                    <Flex mx={2} display={"inline-block"} fontSize="xl">
                      {unim.spenderState.isLoading ? (
                        <Spinner m={0} size={"lg"} />
                      ) : (
                        <Flex>
                          {`balance: `} <Spacer />
                          {unim.spenderState.data?.balance
                            ? web3ctx.web3.utils.fromWei(
                                unim.spenderState.data?.balance,
                                "ether"
                              )
                            : "0"}
                        </Flex>
                      )}
                    </Flex>
                  </code>
                </Flex>
              </HStack>
            </Badge>
          </Flex>
          <Spacer />
          <Flex direction={"column"}>
            <Badge
              colorScheme={"pink"}
              variant={"solid"}
              fontSize={"md"}
              borderRadius={"md"}
              mr={2}
              p={1}
            >
              <Flex>
                <Image
                  ml={2}
                  alt={"rbw"}
                  h="48px"
                  src="https://www.cryptounicorns.fun/static/media/icon_RBW.522bf8ec43ae2c866ee6.png"
                />
                <Flex direction={"column"} wrap="nowrap" w="100%">
                  <code>
                    <Flex mx={2} mt={2} display={"inline-block"} fontSize="xl">
                      {rbw.spenderState.isLoading ? (
                        <Spinner m={0} size={"lg"} />
                      ) : (
                        <Flex>
                          {`balance: `} <Spacer />
                          {rbw.spenderState.data?.balance
                            ? web3ctx.web3.utils.fromWei(
                                rbw.spenderState.data?.balance,
                                "ether"
                              )
                            : "0"}
                        </Flex>
                      )}
                    </Flex>
                  </code>
                </Flex>
              </Flex>
            </Badge>
          </Flex>
        </Flex>
        <code style={{ alignSelf: "center" }}>
          <Text
            p={8}
            textColor={"gray.600"}
            maxW="1337px"
            alignSelf={"center"}
            textAlign="center"
          >
            {" "}
            Use this form to stash any amount of UNIM and RBW into Crypto
            Unicorns.
          </Text>
          <Text mb={4}>
            WARNING: Only use an account with which you have already logged into
            the game. Otherwise, the game server will not respect your stash
            operation.
          </Text>
        </code>
        <Center>
          <code>
            <Stack p={4} bgColor={"blue.1200"} spacing={2}>
              <Box w="100%">
                <FormLabel mb="8px" wordBreak={"break-all"} w="fit-content">
                  {"UNIM to stash"}
                </FormLabel>

                <InputGroup
                  textColor={"blue.900"}
                  size={"lg"}
                  fontSize={"sm"}
                  w="100%"
                  variant={"outline"}
                >
                  <Flex direction={"row"} w="100%" minW="580px">
                    <FormControl isInvalid={notEnoughUNIM}>
                      <Input
                        w="300px"
                        variant={"outline"}
                        type="search"
                        value={unimToStash}
                        isDisabled={
                          unim.setSpenderAllowance.isLoading ||
                          stashUnim.isLoading
                        }
                        onKeyPress={handleKeypress}
                        onChange={(event) => {
                          if (
                            event.target.value.match(/^[0-9]+$/) != null ||
                            event.target.value.length == 0
                          ) {
                            setUNIMToStash(event.target.value);
                          }
                        }}
                      />
                      <FormErrorMessage color="red.400" pl="1">
                        Not enough UNIM
                      </FormErrorMessage>
                    </FormControl>
                    <Spacer />
                    <Button
                      mx={4}
                      isDisabled={
                        (!needAllowanceUNIM || unimToStash === "") &&
                        (notEnoughUNIM || unimToStash == "")
                      }
                      size="md"
                      variant="outline"
                      isLoading={
                        unim.setSpenderAllowance.isLoading ||
                        stashUnim.isLoading
                      }
                      w="220px"
                      colorScheme={"orange"}
                      onClick={() => {
                        if (needAllowanceUNIM) {
                          unim.setSpenderAllowance.mutate(MAX_INT, {
                            onSettled: () => {
                              unim.spenderState.refetch();
                            },
                          });
                        } else {
                          stashUnim.mutate(unimToStash, {
                            onSettled: () => {
                              unim.spenderState.refetch();
                              setUNIMToStash("");
                            },
                          });
                        }
                      }}
                    >
                      {needAllowanceUNIM ? "Set allowance" : "Stash!"}
                    </Button>
                  </Flex>
                </InputGroup>
              </Box>
              <Box w="100%">
                <FormLabel mb="8px" wordBreak={"break-all"} w="fit-content">
                  {"RBW to stash"}
                </FormLabel>

                <InputGroup
                  textColor={"blue.900"}
                  size={"lg"}
                  fontSize={"sm"}
                  w="100%"
                  variant={"outline"}
                >
                  <Flex direction={"row"} w="100%" minW="580px">
                    <FormControl isInvalid={notEnoughRBW}>
                      <Input
                        w="300px"
                        variant={"outline"}
                        isDisabled={
                          rbw.setSpenderAllowance.isLoading ||
                          stashRBW.isLoading
                        }
                        type="search"
                        value={rbwToStash}
                        onKeyPress={handleKeypress}
                        onChange={(event) => {
                          console.log(
                            event.target.value.match(/^[0-9]+$/) != null
                          );
                          if (
                            event.target.value.match(/^[0-9]+$/) != null ||
                            event.target.value.length == 0
                          ) {
                            setRBWToStash(event.target.value);
                          }
                        }}
                      />
                      <FormErrorMessage color="red.400" pl="1">
                        Not enough RBW
                      </FormErrorMessage>
                    </FormControl>
                    <Spacer />
                    <Button
                      mx={4}
                      isDisabled={
                        (!needAllowanceRBW || rbwToStash === "") &&
                        (notEnoughRBW || rbwToStash == "")
                      }
                      size="md"
                      variant="outline"
                      isLoading={
                        rbw.setSpenderAllowance.isLoading || stashRBW.isLoading
                      }
                      w="220px"
                      colorScheme={"orange"}
                      onClick={() => {
                        if (needAllowanceRBW) {
                          rbw.setSpenderAllowance.mutate(MAX_INT, {
                            onSettled: () => {
                              rbw.spenderState.refetch();
                            },
                          });
                        } else {
                          stashRBW.mutate(rbwToStash, {
                            onSettled: () => {
                              rbw.spenderState.refetch();
                              setRBWToStash("");
                            },
                          });
                        }
                      }}
                    >
                      {needAllowanceRBW ? "Set allowance" : "Stash!"}
                    </Button>
                  </Flex>
                </InputGroup>
              </Box>
              {/* </Box> */}
            </Stack>
          </code>
        </Center>
        <Flex
          w="100%"
          direction={"row"}
          flexWrap="wrap"
          mt={10}
          mb={12}
          bgColor="pink.500"
          borderRadius={"xl"}
          boxShadow="xl"
          placeItems={"center"}
        >
          <Text
            mx={2}
            mt={2}
            py={2}
            pl={4}
            display={"inline-block"}
            fontSize="3xl"
            fontWeight="semibold"
          >
            Inventory
          </Text>
        </Flex>
        <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={12} pb={10}>
          <GridItem>
            <LootboxCard
              imageUrl="https://lh3.googleusercontent.com/0H9500IgQKZqKstSo-nruV9RMV9aw7oPtgLARWtbIBU6brTaaK2F0Lk3t7xLygvk80r6OlsBOjnqIhr3EFzEMdwUZlIXTuuEa-O3uQ=w600"
              lootboxType="Common"
              lootboxBalance={lootboxBalances["common"]}
            />
          </GridItem>
          <GridItem>
            <LootboxCard
              imageUrl="https://lh3.googleusercontent.com/1RFVPV0nYzXG0FYea6BQacjsJlbutQSib258tWnovbsIiNhUyOo_BO_AfANN6aSppzvS7ZLpgNcppXuhLOHT2wQAxqAx-Da5bVLnsw=w600"
              lootboxType="Rare"
              lootboxBalance={lootboxBalances["rare"]}
            />
          </GridItem>
          <GridItem>
            <LootboxCard
              imageUrl="https://lh3.googleusercontent.com/2bv26HfU7CgDJhVocABtxbdMLQ8qH2kuU5mQJWVehuNzX-4GiOBm2iIxsTtdriHYpsmr94R7xfRhgELCmnJKQpcMA4wMoPlM_V4zaQ=w600"
              lootboxType="Mythic"
              lootboxBalance={lootboxBalances["mythic"]}
            />
          </GridItem>
          <GridItem>
            <LootboxCard
              imageUrl="https://lh3.googleusercontent.com/2AVqj_GOKf358s0Fkw66MHxEcivOWfvRjAMdmqhHgh3RwyWyJNbnn_amPUJt4KDeO6H7IdWKSV1tli5ijkgHHAemxYGuTof5WZo3wA=w600"
              lootboxType="Land"
              lootboxBalance={lootboxBalances["land"]}
            />
          </GridItem>
          <GridItem>
            <LootboxCard
              imageUrl="https://lh3.googleusercontent.com/30YXRt8oPvD0J9KuRiUTLrRxrigwvbs8P5uFIkJt65hmlVAerYAsxZgPHjvA-byTXseTKJQsnpbuD7giChaO4TyoFm7pcqza8NrZ=w600"
              lootboxType="Mystery"
              lootboxBalance={lootboxBalances["mystery"]}
            />
          </GridItem>
          <GridItem>
            <LootboxCard
              imageUrl="https://lh3.googleusercontent.com/u_BYIeFDCF4dC4n_Col8e1W_dNTK84uMfR6mhjLhQj7GuObvBeENqSu7L8nzDFJ9JDdpiezHpRP0PJ8ioPxOakvU3iz5lbhJy1abRWM=w600"
              lootboxType="RMP"
              lootboxBalance={lootboxBalances["RMP"]}
            />
          </GridItem>
        </Grid>
      </Flex>
    </Flex>
  );
};

export async function getStaticProps() {
  const metatags = {
    title: "Moonstream player portal: crypto unicorns",
    description: "Stash RBW and UNIM in game now!",
  };
  return {
    props: { metaTags: { DEFAULT_METATAGS, ...metatags } },
  };
}

CryptoUnicorns.getLayout = getLayout;

export default CryptoUnicorns;
