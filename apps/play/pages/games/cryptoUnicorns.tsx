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
} from "@chakra-ui/react";
const StashABI = require("../../games/cu/StashABI.json");
import { StashABI as StashABIType } from "../../games/cu/StashABI";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
import { supportedChains } from "../../../../types/Moonstream";
import { useERC20, useToast } from "moonstream-components/src/core/hooks";
import { useMutation, useQuery } from "react-query";
import { DEFAULT_METATAGS } from "../../src/constants";

const contractsAddr: { [key in supportedChains]: string } = {
  mumbai: "0x762aF8cbE298bbFE568BBB6709f854A01c07333D",
  polygon: "0x94f557dDdb245b11d031F57BA7F2C4f28C4A203e",
  ethereum: "0x0000000000000000000000000000000000000000",
  localhost: "0x0000000000000000000000000000000000000000",
};
const CryptoUnicorns = () => {
  const [notEnoughRBW, setNotEnoughRBW] = React.useState(false);
  const [notEnoughUNIM, setNotEnoughUNIM] = React.useState(false);
  const [needAllowanceRBW, setNeedAllowanceRBW] = React.useState(false);
  const [needAllowanceUNIM, setNeedAllowanceUNIM] = React.useState(false);
  const [rbwToStash, setRBWToStash] = React.useState("");
  const [unimToStash, setUNIMToStash] = React.useState("");

  const web3ctx = useContext(Web3Context);

  const getSomthing = async () => {
    const contract = new web3ctx.web3.eth.Contract(
      StashABI
    ) as any as StashABIType;

    contract.options.address =
      contractsAddr[
        web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
      ];
    const rbwAddress = await contract.methods.getRBWAddress().call();
    const unimAddress = await contract.methods.getUNIMAddress().call();
    const gameServer = await contract.methods.getGameServer().call();
    return { rbwAddress, unimAddress, gameServer };
  };

  const stashContract = useQuery(
    [
      "stashContract",
      contractsAddr[
        web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
      ],
    ],
    getSomthing
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

  const contract = new web3ctx.web3.eth.Contract(
    StashABI
  ) as any as StashABIType;

  contract.options.address =
    contractsAddr[
      web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
    ];

  // const web3call = async ({
  //   amountUnim,
  //   amountRBW,
  // }: {
  //   amountUnim: string;
  //   amountRBW: string;
  // }) => {
  //   const response = await

  //   return response;
  // };

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
              <Flex>
                <Image
                  ml={2}
                  alt={"bottle"}
                  h="96px"
                  src="https://darkforest.cryptounicorns.fun/static/media/icon_milk.6fc3d44e.png"
                />
                <Flex direction={"column"} wrap="nowrap" w="100%">
                  <code>
                    <Text mx={2} mt={2} display={"inline-block"} fontSize="xl">
                      {unim.spenderState.isLoading ? (
                        <Spinner m={0} size={"lg"} />
                      ) : (
                        <Flex>
                          {`allowance: `} <Spacer />
                          {unim.spenderState.data?.allowance
                            ? web3ctx.web3.utils.fromWei(
                                unim.spenderState.data?.allowance,
                                "ether"
                              )
                            : "0"}
                        </Flex>
                      )}
                    </Text>
                  </code>{" "}
                  <code>
                    <Text mx={2} mt={2} display={"inline-block"} fontSize="xl">
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
              </Flex>
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
              mt={2}
              p={1}
            >
              <Flex>
                <Image
                  ml={2}
                  alt={"rbw"}
                  h="96px"
                  src="https://www.cryptounicorns.fun/static/media/icon_RBW.522bf8ec43ae2c866ee6.png"
                />
                <Flex direction={"column"} wrap="nowrap" w="100%">
                  <code>
                    <Text mx={2} mt={2} display={"inline-block"} fontSize="xl">
                      {rbw.spenderState.isLoading ? (
                        <Spinner m={0} size={"lg"} />
                      ) : (
                        <Flex>
                          {`allowance: `} <Spacer />
                          {rbw.spenderState.data?.allowance
                            ? web3ctx.web3.utils.fromWei(
                                rbw.spenderState.data?.allowance,
                                "ether"
                              )
                            : "0"}
                        </Flex>
                      )}
                    </Text>
                  </code>{" "}
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
                          unim.setSpenderAllowance.mutate(
                            web3ctx.web3.utils.toWei(unimToStash, "ether"),
                            {
                              onSettled: () => {
                                unim.spenderState.refetch();
                              },
                            }
                          );
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
                          rbw.setSpenderAllowance.mutate(
                            web3ctx.web3.utils.toWei(rbwToStash, "ether"),
                            {
                              onSettled: () => {
                                rbw.spenderState.refetch();
                              },
                            }
                          );
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
