import React, { useContext } from "react";

import {
  Flex,
  Skeleton,
  Stack,
  Editable,
  EditablePreview,
  EditableInput,
  Heading,
  Box,
  Button,
  Spacer,
  SlideFade,
  chakra,
} from "@chakra-ui/react";
import { MockTerminus } from "../../../../types/contracts/MockTerminus";
import { useTerminusContract } from "../core/hooks/useTerminusContract";
import Web3Context from "../core/providers/Web3Provider/context";
import { getMethodsABI, targetChain } from "../core/providers/Web3Provider";
import dynamic from "next/dynamic";
import Web3MethodForm from "./Web3MethodForm";
import useLink from "../core/hooks/useLink";
import Metadata from "./Metadata";
const terminusABI = require("../../../../abi/MockTerminus.json");
const STATES = {
  mint: 2,
  batchMint: 3,
};

const ReactJson = dynamic(() => import("react-json-view"), {
  ssr: false,
});

const TerminuPool = ({
  address,
  poolId,
  ...props
}: {
  address: string;
  poolId: string;
}) => {
  const [isOpen, onOpen] = React.useState(false);
  const [state, setState] = React.useState(STATES.mint);
  const web3ctx = useContext(Web3Context);
  const { poolState, setPoolURI, poolURI, setPoolController } =
    useTerminusContract({
      poolId: poolId,
      ctx: web3ctx,
      address: address,
      targetChain: targetChain,
    });
  const uri = useLink({ link: poolState.data?.uri });
  return (
    <Flex
      className="TerminuPool"
      direction={"row"}
      bgColor="blue.1000"
      flexWrap={"wrap"}
      pt={4}
      px={2}
      {...props}
    >
      <Metadata
        boxShadow={"md"}
        flexGrow={1}
        flexShrink={1}
        flexBasis="150px"
        minW="320px"
        borderRadius="md"
        borderColor={"blue.1200"}
        borderWidth={"3px"}
        p={4}
        mx={4}
        my={2}
        h="420px"
        maxW="420px"
        bgImage={"gray.200"}
        metadata={uri.data}
      />

      <Flex flexGrow={1} flexBasis="500px" direction={"column"}>
        <Heading size="sm" borderBottomWidth={1} w="100%">
          Pool id {poolId}
        </Heading>
        <Stack direction={"column"} py={4}>
          <code key={"Controller"}>
            Controller:
            <Skeleton
              colorScheme={"orange"}
              isLoaded={!poolState.isLoading && !setPoolController.isLoading}
            >
              <Editable
                submitOnBlur={false}
                bgColor={"blue.700"}
                size="sm"
                fontSize={"sm"}
                textColor="gray.500"
                w="100%"
                minW={["280px", "300px", "360px", "420px", null]}
                variant={"outline"}
                selectAllOnFocus={true}
                placeholder={poolState.data?.controller}
                defaultValue={poolState.data?.controller}
                isDisabled={poolState.data?.controller !== web3ctx.account}
                onSubmit={(nextValue) => {
                  setPoolController.mutate(
                    { newController: nextValue, poolId: poolId },
                    {
                      onSettled: () => {
                        poolState.refetch();
                      },
                    }
                  );
                }}
              >
                <EditablePreview w="100%" px={2} cursor={"text"} />
                <EditableInput wordBreak={"keep-all"} w="100%" px={2} />
              </Editable>
            </Skeleton>
          </code>
          <code key={"Supply"}>
            Supply:
            <Flex
              px={2}
              fontSize="16px"
              h="27px"
              bgColor={"blue.700"}
              alignItems="center"
              wordBreak={"break-all"}
            >
              {poolState.data?.supply} <Spacer />{" "}
              <Button
                size="xs"
                variant={"ghost"}
                py={1}
                colorScheme="orange"
                onClick={() => {
                  if (state === STATES.mint) {
                    onOpen((current) => !current);
                  } else {
                    setState(() => STATES.mint);
                    onOpen(true);
                  }
                }}
              >
                Mint more supply
              </Button>
            </Flex>
            {state != 0 && (
              <SlideFade in={isOpen}>
                <Flex
                  w="100%"
                  transition={"1s"}
                  display={isOpen ? "flex" : "none"}
                  m={0}
                  justifyContent="center"
                  flexGrow={1}
                  key={state}
                >
                  {state === STATES.mint && (
                    <Web3MethodForm
                      w="100%"
                      bgColor="blue.700"
                      key={`cp-Web3MethodForm-mint`}
                      onSuccess={() => {
                        poolState.refetch();
                      }}
                      rendered={true}
                      hide={["data", "poolID"]}
                      argumentFields={{
                        data: {
                          placeholder: "",
                          initialValue: web3ctx.web3.utils.utf8ToHex(""),
                        },
                        poolID: {
                          placeholder: "",
                          initialValue: poolId,
                        },
                      }}
                      method={getMethodsABI<MockTerminus["methods"]>(
                        terminusABI,
                        "mint"
                      )}
                      contractAddress={address}
                    />
                  )}
                </Flex>
              </SlideFade>
            )}
          </code>
          <code key={"capacity"}>
            Capacity:
            <Flex
              px={2}
              fontSize="16px"
              w="100%"
              maxW="100%"
              bgColor={"blue.700"}
              alignItems="center"
              wordBreak={"break-all"}
            >
              {poolState.data?.capacity} <Spacer />{" "}
            </Flex>
          </code>
          <code key={"uri"}>
            URI:
            <Skeleton
              colorScheme={"orange"}
              isLoaded={!poolState.isLoading && !setPoolURI.isLoading}
            >
              <Editable
                submitOnBlur={false}
                bgColor={"blue.700"}
                size="sm"
                fontSize={"sm"}
                h="27px"
                textColor="gray.500"
                w="100%"
                minW={["280px", "300px", "360px", "420px", null]}
                variant={"outline"}
                isDisabled={poolState.data?.controller !== web3ctx.account}
                defaultValue={poolState.data?.uri}
                placeholder="Set URI here"
                selectAllOnFocus={true}
                onSubmit={(nextValue) => {
                  setPoolURI.mutate(
                    { uri: nextValue, poolId: poolId },
                    {
                      onSettled: () => {
                        poolState.refetch();
                      },
                    }
                  );
                }}
              >
                <EditablePreview w="100%" px={2} cursor="text" />
                <EditableInput w="100%" px={2} />
              </Editable>
            </Skeleton>
          </code>
          <Skeleton isLoaded={!poolURI.isLoading}>
            {poolURI?.data && (
              <Box cursor="crosshair" overflowWrap={"break-word"}>
                <ReactJson
                  name="metadata"
                  collapsed
                  style={{
                    cursor: "text",
                    lineBreak: "anywhere",
                  }}
                  src={poolURI?.data}
                  theme="harmonic"
                  displayDataTypes={false}
                  displayObjectSize={false}
                  collapseStringsAfterLength={128}
                />
              </Box>
            )}
          </Skeleton>
        </Stack>
      </Flex>
    </Flex>
  );
};

export default chakra(React.memo(TerminuPool));
