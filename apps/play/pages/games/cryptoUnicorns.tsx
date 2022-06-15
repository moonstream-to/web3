import React, { useContext } from "react";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
import {
  Flex,
  Center,
  Badge,
  Spacer,
  Image,
  Spinner,
  Text,
} from "@chakra-ui/react";
import Web3MethodForm from "moonstream-components/src/components/Web3MethodForm";
const StashABI = require("../../games/cu/StashABI.json");
import { StashABI as StashABIType } from "../../games/cu/StashABI";
import { getMethodsABI } from "moonstream-components/src/core/providers/Web3Provider";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
import { supportedChains } from "../../../../types/Moonstream";
import { useERC20 } from "moonstream-components/src/core/hooks";

const contractsAddr: { [key in supportedChains]: string } = {
  mumbai: "0x762aF8cbE298bbFE568BBB6709f854A01c07333D",
  polygon: "0x762aF8cbE298bbFE568BBB6709f854A01c07333D",
  ethereum: "non-supported",
  localhost: "non-supported",
};
const rbwAddr: { [key in supportedChains]: string } = {
  mumbai: "0x4Df452487E6c9d0C3Dc5EB4936244F8572b3F0b6",
  polygon: "0x431CD3C9AC9Fc73644BF68bF5691f4B83F9E104f",
  ethereum: "",
  localhost: "",
};

const unimAddr: { [key in supportedChains]: string } = {
  mumbai: "0x47d0f0BD94188e3f8c6fF2C0B1Bf7D6D8BED7534",
  polygon: "0x64060aB139Feaae7f06Ca4E63189D86aDEb51691",
  ethereum: "",
  localhost: "",
};
const CryptoUnicorns = () => {
  const web3ctx = useContext(Web3Context);
  const rbw = useERC20({
    contractAddress:
      rbwAddr[
        web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
      ],
    ctx: web3ctx,
  });
  const unim = useERC20({
    contractAddress:
      unimAddr[
        web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
      ],
    ctx: web3ctx,
  });
  return (
    <Flex className="Games" borderRadius={"xl"} bgColor={"blue.1000"}>
      <Flex w="100%" minH="100vh" direction={"column"} px="7%" mt="100px">
        <Flex w="100%" direction={"row"} flexWrap="wrap" mb={12}>
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
                h="48px"
                src="https://darkforest.cryptounicorns.fun/static/media/icon_milk.6fc3d44e.png"
              />
              <code>
                <Text mx={2} mt={2} display={"inline-block"} fontSize="xl">
                  {unim.ERC20State.isLoading ? (
                    <Spinner m={0} size={"lg"} />
                  ) : unim.ERC20State.data?.balance ? (
                    web3ctx.web3.utils.fromWei(
                      unim.ERC20State.data?.balance,
                      "ether"
                    )
                  ) : (
                    "0"
                  )}{" "}
                  UNIM
                </Text>
              </code>
            </Flex>
          </Badge>
          <Spacer />
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
              <code>
                <Text mx={2} mt={2} display={"inline-block"} fontSize="xl">
                  {rbw.ERC20State.isLoading ? (
                    <Spinner m={0} size={"lg"} />
                  ) : rbw.ERC20State.data?.balance ? (
                    web3ctx.web3.utils.fromWei(
                      rbw.ERC20State.data?.balance,
                      "ether"
                    )
                  ) : (
                    "0"
                  )}{" "}
                  RBW
                </Text>
              </code>
            </Flex>
          </Badge>
        </Flex>
        <code>
          <Text
            p={8}
            textColor={"gray.600"}
            maxW="1337px"
            alignSelf={"center"}
            textAlign="justify"
          >
            {" "}
            Use this form to stash any amount of UNIM and RBW into Crypto
            Unicorns.
          </Text>
        </code>
        <Center>
          <code>
            <Web3MethodForm
              w="100%"
              bgColor="blue.600"
              borderRadius={"lg"}
              dropShadow="2xl"
              maxW="620px"
              p={4}
              title="Stash your RBW and UNIM!"
              key={`cp-Web3MethodForm-mint`}
              minW="unset"
              inputsProps={{ size: "lg" }}
              onSuccess={() => {
                // poolState.refetch();
              }}
              rendered={true}
              hide={["data", "poolID"]}
              argumentFields={{
                amountUNIM: { label: "Amount UNIM", valueIsEther: true },
                amountRBW: { label: "Amount RBW", valueIsEther: true },
                // data: {
                //   placeholder: "",
                //   initialValue: web3ctx.web3.utils.utf8ToHex(""),
                // },
                // poolID: {
                //   placeholder: "",
                //   initialValue: poolId,
                // },
              }}
              method={getMethodsABI<StashABIType["methods"]>(
                StashABI,
                "stashUNIMAndRBW"
              )}
              contractAddress={
                web3ctx.targetChain?.name
                  ? contractsAddr[
                      web3ctx.targetChain.name as any as supportedChains
                    ]
                  : ""
              }
            />
          </code>
        </Center>
      </Flex>
    </Flex>
  );
};

CryptoUnicorns.getLayout = getLayout;

export default CryptoUnicorns;
