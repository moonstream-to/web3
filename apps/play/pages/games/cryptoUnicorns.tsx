import React, { useContext } from "react";
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
  VStack
} from "@chakra-ui/react";
const StashABI = require("../../games/cu/StashABI.json");
import { StashABI as StashABIType } from "../../games/cu/StashABI";
const GameBankABI = require("../../games/cu/GameBankABI.json");
import { GameBankABI as GameBankABIType, LootBoxStashed } from "../../games/cu/GameBankABI";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
import useTerminusContract from "moonstream-components/src/core/hooks/useTerminusContract";
import { supportedChains } from "../../../../types/Moonstream";
import { useERC20, useToast } from "moonstream-components/src/core/hooks";
import { useMutation, useQuery } from "react-query";
import { DEFAULT_METATAGS } from "../../src/constants";
import { MAX_INT } from "moonstream-components/src/core/providers/Web3Provider";
import LootboxCard from "../../../../packages/moonstream-components/src/components/CryptoUnicorns/LootboxCard";

const contractsAddr: { [key in supportedChains]: string } = {
  mumbai: "0x762aF8cbE298bbFE568BBB6709f854A01c07333D",
  polygon: "0x94f557dDdb245b11d031F57BA7F2C4f28C4A203e",
  ethereum: "0x0000000000000000000000000000000000000000",
  localhost: "0x0000000000000000000000000000000000000000",
};

type LootboxType = "common" | "rare" | "mythic" | "land" | "mystery" | "RMP";
interface LootboxInfo { 
  label: string;
  imageUri: string;
  poolIdByChain: {
    [key in supportedChains]: number;
  };
};

// const lootboxPoolIdsByBlockchain: { [key in supportedChains]: any } = {
//   mumbai: "0x762aF8cbE298bbFE568BBB6709f854A01c07333D",
//   polygon: "0x94f557dDdb245b11d031F57BA7F2C4f28C4A203e",
//   ethereum: "0x0000000000000000000000000000000000000000",
//   localhost: "0x0000000000000000000000000000000000000000",
// };

const lootboxInfo: { [key in LootboxType]: LootboxInfo} = {
  common: {
    label: "common lootbox",
    imageUri: "",
    poolIdByChain: {
      mumbai: -1,
      polygon: 4,
      ethereum: -1,
      localhost: -1,
    },
  },
};


const CryptoUnicorns = () => {
  const [notEnoughRBW, setNotEnoughRBW] = React.useState(false);
  const [notEnoughUNIM, setNotEnoughUNIM] = React.useState(false);
  const [needAllowanceRBW, setNeedAllowanceRBW] = React.useState(false);
  const [needAllowanceUNIM, setNeedAllowanceUNIM] = React.useState(false);
  const [rbwToStash, setRBWToStash] = React.useState("");
  const [unimToStash, setUNIMToStash] = React.useState("");

  const web3ctx = useContext(Web3Context);

  // const terminus = useTerminusContract({
  //   poolId: ,
  //   address: contractAddress,
  //   ctx: web3ctx,
  // });

  const getGameBankConfig = async () => {
    const contract = new web3ctx.web3.eth.Contract(
      StashABI
    ) as any as StashABIType;

    const gameBankContract = new web3ctx.web3.eth.Contract(
      GameBankABI
    ) as unknown as GameBankABIType;

    contract.options.address =
      contractsAddr[
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
      contractsAddr[
      web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
      ],
    ],
    getGameBankConfig
  );

  const rbw = useERC20({
    contractAddress: stashContract.data?.rbwAddress,
    ctx: web3ctx,
    spender:
      contractsAddr[
      web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
      ],
  });
  const unim = useERC20({
    contractAddress: stashContract.data?.unimAddress,
    spender:
      contractsAddr[
      web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
      ],
    ctx: web3ctx,
  });

  // const terminusPools: { [key in LootboxType]: any} = {
  //   common: useTerminusContract({
  //     poolId: "",
  //     address: String(stashContract.data?.terminusAddress),
  //     ctx: web3ctx,
  //   }),
  // };

  const contract = new web3ctx.web3.eth.Contract(
    StashABI
  ) as any as StashABIType;

  contract.options.address =
    contractsAddr[
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

  const handleSubmit = () => { };

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
                    <Text mx={2} display={"inline-block"} fontSize="xl">
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
                    </Text>
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
                    <Text mx={2} mt={2} display={"inline-block"} fontSize="xl">
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
                    </Text>
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
                          console.log(
                            event.target.value.match(/^[0-9]+$/) != null
                          );
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
        <Flex mb={12} wrap="wrap" direction="row" justifyContent="left" pb={10}>
          <LootboxCard
            imageUrl="https://lh3.googleusercontent.com/0H9500IgQKZqKstSo-nruV9RMV9aw7oPtgLARWtbIBU6brTaaK2F0Lk3t7xLygvk80r6OlsBOjnqIhr3EFzEMdwUZlIXTuuEa-O3uQ=w600"
            lootboxType="Common"
            lootboxBalance={4}
          />
          <LootboxCard
            imageUrl="https://lh3.googleusercontent.com/1RFVPV0nYzXG0FYea6BQacjsJlbutQSib258tWnovbsIiNhUyOo_BO_AfANN6aSppzvS7ZLpgNcppXuhLOHT2wQAxqAx-Da5bVLnsw=w600"
            lootboxType="Rare"
            lootboxBalance={12}
          />
          <LootboxCard
            imageUrl="https://lh3.googleusercontent.com/2bv26HfU7CgDJhVocABtxbdMLQ8qH2kuU5mQJWVehuNzX-4GiOBm2iIxsTtdriHYpsmr94R7xfRhgELCmnJKQpcMA4wMoPlM_V4zaQ=w600"
            lootboxType="Mythic"
            lootboxBalance={21}
          />
          <LootboxCard
            imageUrl="https://lh3.googleusercontent.com/2AVqj_GOKf358s0Fkw66MHxEcivOWfvRjAMdmqhHgh3RwyWyJNbnn_amPUJt4KDeO6H7IdWKSV1tli5ijkgHHAemxYGuTof5WZo3wA=w600"
            lootboxType="Land"
            lootboxBalance={0}
          />
          <LootboxCard
            imageUrl="https://lh3.googleusercontent.com/30YXRt8oPvD0J9KuRiUTLrRxrigwvbs8P5uFIkJt65hmlVAerYAsxZgPHjvA-byTXseTKJQsnpbuD7giChaO4TyoFm7pcqza8NrZ=w600"
            lootboxType="Mystery"
            lootboxBalance={7}
          />
          <LootboxCard
            imageUrl="https://lh3.googleusercontent.com/u_BYIeFDCF4dC4n_Col8e1W_dNTK84uMfR6mhjLhQj7GuObvBeENqSu7L8nzDFJ9JDdpiezHpRP0PJ8ioPxOakvU3iz5lbhJy1abRWM=w600"
            lootboxType="RMP"
            lootboxBalance={1}
          />
        </Flex>
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
