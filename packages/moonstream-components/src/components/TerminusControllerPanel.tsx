import React, { useContext } from "react";
import {
  Flex,
  Button,
  chakra,
  Stack,
  Spinner,
  Editable,
  EditablePreview,
  EditableInput,
  Skeleton,
  Text,
  ButtonGroup,
  SlideFade,
  FlexProps,
  Box,
} from "@chakra-ui/react";
import { getMethodsABI } from "../core/providers/Web3Provider";
import { useTerminusContract } from "../core/hooks/useTerminusContract";
import Web3Context from "../core/providers/Web3Provider/context";
import { MockTerminus } from "../../../../types/contracts/MockTerminus";
import Web3MethodForm from "./Web3MethodForm";
import dynamic from "next/dynamic";
const ReactJson = dynamic(() => import("react-json-view"), {
  ssr: false,
});
const terminusABI = require("../../../../abi/MockTerminus.json");
const STATES = {
  withdraw: 1,
  createPool: 2,
};
const TerminusControllerPanel = ({
  address,
  isController,
  ...props
}: {
  isController: boolean;
  address: string;
}) => {
  const web3ctx = useContext(Web3Context);
  const terminus = useTerminusContract({
    address: address,
    ctx: web3ctx,
  });

  const [isOpen, onOpen] = React.useState(false);
  const [state, setState] = React.useState(STATES.createPool);

  if (terminus.contractState.isLoading || terminus.paymentToken.isLoading)
    return <Spinner />;
  return (
    <>
      <Flex {...props}>
        <Stack direction={"column"} w="100%">
          <Flex
            justifyContent={"center"}
            fontWeight="600"
            textColor={"blue.50"}
            direction="column"
            px={4}
          >
            <Stack direction={"column"} py={4}>
              <code key={"URI"}>
                URI:
                <Editable
                  submitOnBlur={false}
                  bgColor={"blue.700"}
                  size="sm"
                  fontSize={"sm"}
                  textColor="gray.500"
                  w="100%"
                  minW={["280px", "300px", "360px", "420px", null]}
                  variant={"outline"}
                  placeholder={terminus.contractState.data?.contractURI}
                  defaultValue={terminus.contractState.data?.contractURI}
                  isDisabled={terminus.setURI.isLoading || !isController}
                  onSubmit={(nextValue) => {
                    terminus.setURI.mutate({ uri: nextValue });
                  }}
                >
                  <Skeleton
                    colorScheme={"orange"}
                    isLoaded={
                      !terminus.contractState.isLoading &&
                      !terminus.setURI.isLoading
                    }
                  >
                    <EditablePreview w="100%" px={2} />
                    <EditableInput w="100%" px={2} />
                  </Skeleton>
                </Editable>
              </code>
              <code key={"BasePrice"}>
                Pool Base Price:
                <Editable
                  submitOnBlur={false}
                  bgColor={"blue.700"}
                  size="sm"
                  fontSize={"sm"}
                  textColor="gray.500"
                  w="100%"
                  minW={["280px", "300px", "360px", "420px", null]}
                  variant={"outline"}
                  placeholder={terminus.contractState.data?.poolBasePrice}
                  defaultValue={terminus.contractState.data?.poolBasePrice}
                  isDisabled={
                    terminus.setPoolBasePrice.isLoading || !isController
                  }
                  onSubmit={(nextValue) => {
                    terminus.setPoolBasePrice.mutate(nextValue);
                  }}
                >
                  <Skeleton
                    colorScheme={"orange"}
                    isLoaded={
                      !terminus.contractState.isLoading &&
                      !terminus.setPoolBasePrice.isLoading
                    }
                  >
                    <EditablePreview w="100%" px={2} />
                    <EditableInput w="100%" px={2} />
                  </Skeleton>
                </Editable>
              </code>
              <code key={"PaymentToken"}>
                Payment token:
                <Editable
                  submitOnBlur={false}
                  bgColor={"blue.700"}
                  size="sm"
                  fontSize={"sm"}
                  textColor="gray.500"
                  w="100%"
                  minW={["280px", "300px", "360px", "420px", null]}
                  variant={"outline"}
                  placeholder={terminus.contractState.data?.paymentToken}
                  defaultValue={terminus.contractState.data?.paymentToken}
                  isDisabled={
                    terminus.setPoolBasePrice.isLoading || !isController
                  }
                  onSubmit={(nextValue) => {
                    terminus.setPaymentToken.mutate(nextValue);
                  }}
                >
                  <Skeleton
                    colorScheme={"orange"}
                    isLoaded={
                      !terminus.contractState.isLoading &&
                      !terminus.setPoolBasePrice.isLoading
                    }
                  >
                    <EditablePreview w="100%" px={2} />
                    <EditableInput w="100%" px={2} />
                  </Skeleton>
                </Editable>
              </code>
              <code key={"PoolController"}>
                Pool controller:
                <Editable
                  submitOnBlur={false}
                  bgColor={"blue.700"}
                  size="sm"
                  fontSize={"sm"}
                  textColor="gray.500"
                  w="100%"
                  minW={["280px", "300px", "360px", "420px", null]}
                  variant={"outline"}
                  placeholder={
                    isController
                      ? "You ;) "
                      : terminus.contractState.data?.controller
                  }
                  defaultValue=""
                  isDisabled={terminus.setController.isLoading || !isController}
                  onSubmit={(nextValue) => {
                    if (web3ctx.web3.utils.isAddress(nextValue)) {
                      terminus.setController.mutate(nextValue);
                    }
                  }}
                >
                  <Skeleton
                    colorScheme={"orange"}
                    isLoaded={
                      !terminus.contractState.isLoading &&
                      !terminus.setController.isLoading
                    }
                  >
                    <EditablePreview w="100%" px={2} />
                    <EditableInput w="100%" px={2} />
                  </Skeleton>
                </Editable>
              </code>
              <code key={"npools"}>
                Number of pools:
                <Skeleton
                  display={"inline"}
                  isLoaded={!terminus.contractState.isLoading}
                >
                  <Text display={"inline"}>
                    {terminus.contractState.data?.totalPools}
                  </Text>
                  <ButtonGroup
                    flexWrap={"wrap"}
                    justifyContent="center"
                    hidden={!isController}
                  >
                    <Button
                      isActive={state === STATES.createPool && isOpen}
                      key={`createpool`}
                      colorScheme={"orange"}
                      size="sm"
                      variant={"ghost"}
                      onClick={() => {
                        if (state === STATES.createPool) {
                          onOpen((current) => !current);
                        } else {
                          setState(() => STATES.createPool);
                          onOpen(true);
                        }
                      }}
                    >
                      Create new pool
                    </Button>
                    <Button
                      isActive={state === STATES.withdraw && isOpen}
                      key={`withdraw`}
                      colorScheme={"orange"}
                      size="sm"
                      variant={"ghost"}
                      onClick={() => {
                        if (state === STATES.withdraw) {
                          onOpen((current) => !current);
                        } else {
                          setState(() => STATES.withdraw);
                          onOpen(true);
                        }
                      }}
                    >
                      withdraw payments
                    </Button>
                  </ButtonGroup>
                </Skeleton>
              </code>
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
                    {state === STATES.withdraw && (
                      <Web3MethodForm
                        w="100%"
                        key={`cp-Web3MethodForm-with`}
                        maxW="660px"
                        onSuccess={() => terminus.contractState.refetch()}
                        rendered={true}
                        hide={["data"]}
                        method={getMethodsABI<MockTerminus["methods"]>(
                          terminusABI,
                          "withdrawPayments"
                        )}
                        contractAddress={address}
                      />
                    )}
                    {state === STATES.createPool && (
                      <Web3MethodForm
                        w="100%"
                        key={`cp-Web3MethodForm-with`}
                        maxW="660px"
                        onSuccess={() => terminus.contractState.refetch()}
                        rendered={true}
                        hide={["data"]}
                        method={getMethodsABI<MockTerminus["methods"]>(
                          terminusABI,
                          "createPoolV1"
                        )}
                        contractAddress={address}
                      />
                    )}
                  </Flex>
                </SlideFade>
              )}
              <Skeleton isLoaded={!terminus.contractJSON.isLoading}>
                {terminus.contractJSON.data && (
                  <Box cursor="crosshair" overflowWrap={"break-word"}>
                    <ReactJson
                      name="metadata"
                      collapsed
                      style={{
                        cursor: "text",
                        lineBreak: "anywhere",
                      }}
                      src={terminus.contractJSON.data}
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
        </Stack>
      </Flex>
    </>
  );
};
export default chakra<any, FlexProps>(TerminusControllerPanel, {
  baseStyle: {
    w: "100%",
    direction: ["column", "row"],
    bgColor: "orange.100",
  },
});
