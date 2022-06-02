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
} from "@chakra-ui/react";
import { getMethodsABI, targetChain } from "../core/providers/Web3Provider";
import { useTerminusContract } from "../core/hooks/useTerminusContract";
import Web3Context from "../core/providers/Web3Provider/context";
import { MockTerminus } from "../../../../types/contracts/MockTerminus";
import Web3MethodForm from "./Web3MethodForm";
const terminusABI = require("../../../../abi/MockTerminus.json");
const STATES = {
  withdraw: 1,
  createPool: 2,
};
const TerminusControllerPanel = ({
  address,
  ...props
}: {
  address: string;
}) => {
  const web3ctx = useContext(Web3Context);
  const terminus = useTerminusContract({
    address: address,
    targetChain: targetChain,
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
            // borderBottomWidth={"2px"}
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
                  isDisabled={terminus.setURI.isLoading}
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
                  isDisabled={terminus.setPoolBasePrice.isLoading}
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
                  isDisabled={terminus.setPoolBasePrice.isLoading}
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
                  placeholder="You ;) "
                  defaultValue=""
                  isDisabled={terminus.setController.isLoading}
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
                  <ButtonGroup flexWrap={"wrap"} justifyContent="center">
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
