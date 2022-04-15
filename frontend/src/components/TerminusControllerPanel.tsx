import React, { FC, useContext } from "react";
import {
  Flex,
  Button,
  chakra,
  Stack,
  Input,
  Fade,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from "@chakra-ui/react";
import { TERMINUS_DIAMOND_ADDRESS } from "../AppDefintions";
import { targetChain } from "../core/providers/Web3Provider";
import { FlexProps } from "@chakra-ui/react";
import useTerminus from "../core/hooks/useTerminus";
import Web3Context from "../core/providers/Web3Provider/context";
import UIContext from "../core/providers/UIProvider/context";

const STATES = {
  buttons: 0,
  transferOwnershipArgs: 1,
  withrawFundsArgs: 2,
  setControllerArgs: 3,
  setPoolBasePriceArgs: 4,
  URIArgs: 5,
  setPaymentTokenArgs: 6,
  newPoolArgs: 7,
};
const TerminusControllerPanel: FC<FlexProps> = (props) => {
  const terminus = useTerminus({
    diamondAddress: TERMINUS_DIAMOND_ADDRESS,
    targetChain: targetChain,
  });

  const [state, setState] = React.useState(STATES.buttons);
  const [address, setAddressField] = React.useState("");
  const [newURI, setNewURI] = React.useState("");
  const [amount, setAmountField] = React.useState(0);
  const handleAddressFieldChange = (event: any) =>
    setAddressField(event.target.value);
  const handleAmountFieldChange = (event: any) => setAmountField(event);
  const handleURIFieldChange = (event: any) => setNewURI(event.target.value);
  const web3Provider = useContext(Web3Context);
  const ui = useContext(UIContext);

  return (
    <>
      {!ui.isMobileView && (
        <Flex {...props}>
          <Stack direction={"column"} w="100%">
            <Flex
              justifyContent={"center"}
              fontWeight="600"
              textColor={"blue.50"}
            >
              Pool controller panel
            </Flex>
            {state === STATES.buttons && (
              <Fade in={state === STATES.buttons ? true : false}>
                <Flex
                  w="100%"
                  justifyContent="space-evenly"
                  direction={["column", "row", null, "row"]}
                  flexWrap="wrap"
                >
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() => setState(STATES.newPoolArgs)}
                  >
                    New Pool
                  </Button>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() => setState(STATES.setControllerArgs)}
                  >
                    Transfer control
                  </Button>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() => setState(STATES.withrawFundsArgs)}
                    isDisabled={
                      Number(
                        terminus.terminusPaymentTokenCache.data?.spenderBalance
                      ) === 0
                    }
                  >
                    Withraw payments
                  </Button>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() => setState(STATES.setPoolBasePriceArgs)}
                  >
                    Set pool price
                  </Button>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() => setState(STATES.URIArgs)}
                  >
                    Set contract URI
                  </Button>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() => setState(STATES.setPaymentTokenArgs)}
                  >
                    Set payment token
                  </Button>
                </Flex>
              </Fade>
            )}
            {state === STATES.setControllerArgs && (
              <Fade in={state === STATES.setControllerArgs ? true : false}>
                <Flex
                  w="100%"
                  justifyContent="center"
                  px={20}
                  alignItems="baseline"
                >
                  <Input
                    value={address}
                    onChange={handleAddressFieldChange}
                    placeholder="New terminus controller address"
                    size="md"
                    maxW="420px"
                    fontSize={"sm"}
                    isDisabled={terminus.setTerminusController.isLoading}
                  />
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() =>
                      terminus.setTerminusController.mutate({
                        newController: address,
                      })
                    }
                    isLoading={terminus.setTerminusController.isLoading}
                  >
                    Submit
                  </Button>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() => setState(STATES.buttons)}
                  >
                    Cancel
                  </Button>
                </Flex>
              </Fade>
            )}
            {state === STATES.setPaymentTokenArgs && (
              <Fade in={state === STATES.setPaymentTokenArgs ? true : false}>
                <Flex
                  w="100%"
                  justifyContent="center"
                  px={20}
                  alignItems="baseline"
                >
                  <Input
                    value={address}
                    onChange={handleAddressFieldChange}
                    placeholder="New terminus controller address"
                    size="md"
                    maxW="420px"
                    fontSize={"sm"}
                    isDisabled={terminus.setPaymentToken.isLoading}
                  />
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() =>
                      terminus.setPaymentToken
                        .mutateAsync({
                          paymentTokenAddress: address,
                        })
                        .then(() => {
                          setAddressField("");
                          setState(STATES.buttons);
                        })
                    }
                    isLoading={terminus.setTerminusController.isLoading}
                  >
                    Submit
                  </Button>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() => setState(STATES.buttons)}
                  >
                    Cancel
                  </Button>
                </Flex>
              </Fade>
            )}
            {state === STATES.withrawFundsArgs && (
              <Fade in={state === STATES.withrawFundsArgs ? true : false}>
                <Flex
                  w="100%"
                  justifyContent="center"
                  px={20}
                  alignItems="center"
                >
                  <Flex bgColor={"gray.300"} borderRadius="md" p={1}>
                    <NumberInput
                      defaultValue={0}
                      precision={1}
                      step={1}
                      onChange={handleAmountFieldChange}
                      value={amount}
                      size="md"
                      mx={2}
                      isDisabled={terminus.withrawPayments.isLoading}
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                    <Slider
                      isDisabled={
                        terminus.withrawPayments.isLoading &&
                        Number(
                          terminus.terminusPaymentTokenCache.data
                            ?.spenderBalance
                        ) > 0
                      }
                      minW="300px"
                      mx={3}
                      flex="1"
                      focusThumbOnChange={false}
                      value={amount}
                      onChange={handleAmountFieldChange}
                      min={0}
                      max={
                        terminus.terminusPaymentTokenCache.data?.spenderBalance
                          ? Number(
                              web3Provider.web3.utils.fromWei(
                                terminus.terminusPaymentTokenCache.data
                                  .spenderBalance,
                                "ether"
                              )
                            ) ?? 0
                          : 0
                      }
                    >
                      <SliderTrack>
                        <SliderFilledTrack />
                      </SliderTrack>
                      <SliderThumb fontSize="sm" boxSize="16px" />
                    </Slider>
                  </Flex>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() =>
                      terminus.withrawPayments
                        .mutateAsync({
                          toAddress: web3Provider.account,
                          amount: web3Provider.web3.utils.toWei(
                            String(amount),
                            "ether"
                          ),
                        })
                        .then(() => {
                          setState(STATES.buttons);
                          setAmountField(0);
                        })
                    }
                    isLoading={terminus.withrawPayments.isLoading}
                  >
                    Submit
                  </Button>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() => setState(STATES.buttons)}
                  >
                    Cancel
                  </Button>
                </Flex>
              </Fade>
            )}
            {state === STATES.setPoolBasePriceArgs && (
              <Fade in={state === STATES.setPoolBasePriceArgs ? true : false}>
                <Flex
                  w="100%"
                  justifyContent="center"
                  px={20}
                  alignItems="center"
                >
                  <Flex
                    bgColor={"gray.300"}
                    borderRadius="md"
                    p={1}
                    alignItems="center"
                  >
                    New pool base price:
                    <NumberInput
                      defaultValue={0}
                      precision={1}
                      step={1}
                      onChange={handleAmountFieldChange}
                      value={amount}
                      size="md"
                      mx={2}
                      isDisabled={terminus.withrawPayments.isLoading}
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </Flex>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() =>
                      terminus.setPoolBasePrice
                        .mutateAsync({
                          newPoolBasePrice: web3Provider.web3.utils.toWei(
                            String(amount),
                            "ether"
                          ),
                        })
                        .then(() => {
                          setState(STATES.buttons);
                          setAmountField(0);
                        })
                    }
                    isLoading={terminus.withrawPayments.isLoading}
                  >
                    Submit
                  </Button>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() => setState(STATES.buttons)}
                  >
                    Cancel
                  </Button>
                </Flex>
              </Fade>
            )}
            {state === STATES.newPoolArgs && (
              <Fade in={state === STATES.newPoolArgs ? true : false}>
                <Flex
                  w="100%"
                  justifyContent="center"
                  px={20}
                  alignItems="center"
                >
                  <Flex
                    bgColor={"gray.300"}
                    borderRadius="md"
                    p={1}
                    alignItems="center"
                  >
                    New pool maximum supply:
                    <NumberInput
                      onChange={handleAmountFieldChange}
                      value={amount}
                      size="md"
                      mx={2}
                      isDisabled={terminus.createPoolMutation.isLoading}
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </Flex>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() =>
                      terminus.createPoolMutation
                        .mutateAsync(String(amount))
                        .then(() => {
                          setState(STATES.buttons);
                          setAmountField(0);
                        })
                    }
                    isLoading={terminus.createPoolMutation.isLoading}
                  >
                    Submit
                  </Button>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() => {
                      setState(STATES.buttons);
                      setAmountField(0);
                    }}
                  >
                    Cancel
                  </Button>
                </Flex>
              </Fade>
            )}
            {state === STATES.URIArgs && (
              <Fade in={state === STATES.URIArgs ? true : false}>
                <Flex
                  w="100%"
                  justifyContent="center"
                  px={20}
                  alignItems="center"
                >
                  <Flex
                    bgColor={"gray.300"}
                    borderRadius="md"
                    p={1}
                    alignItems="center"
                  >
                    <Input
                      value={newURI}
                      onChange={handleURIFieldChange}
                      placeholder="New terminus uri"
                      size="md"
                      minW="420px"
                      maxW="820px"
                      fontSize={"sm"}
                      isDisabled={terminus.setTerminusController.isLoading}
                    />
                  </Flex>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() =>
                      terminus.setURI
                        .mutateAsync({ newURI: newURI })
                        .then(() => {
                          setState(STATES.buttons);
                          setNewURI("");
                        })
                    }
                    isLoading={terminus.withrawPayments.isLoading}
                  >
                    Submit
                  </Button>
                  <Button
                    variant={"solid"}
                    colorScheme={"orange"}
                    onClick={() => setState(STATES.buttons)}
                  >
                    Cancel
                  </Button>
                </Flex>
              </Fade>
            )}
          </Stack>
        </Flex>
      )}
      {ui.isMobileView && (
        <Accordion w="100%" allowToggle>
          <AccordionItem w="100%" {...props}>
            <h2>
              <AccordionButton>
                <Flex
                  justifyContent={"center"}
                  fontWeight="600"
                  textColor={"blue.50"}
                  w="100%"
                >
                  Pool controller panel
                </Flex>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4} minH="100vh">
              <>
                {state === STATES.buttons && (
                  <Fade in={state === STATES.buttons ? true : false}>
                    <Flex
                      w="100%"
                      justifyContent="space-evenly"
                      direction={["column", "row", null, "row"]}
                      flexWrap="wrap"
                    >
                      <Button
                        variant={"solid"}
                        colorScheme={"orange"}
                        w={["100%", "45%", "initial"]}
                        onClick={() => setState(STATES.newPoolArgs)}
                      >
                        New Pool
                      </Button>
                      <Button
                        variant={"solid"}
                        colorScheme={"orange"}
                        w={["100%", "45%", "initial"]}
                        onClick={() => setState(STATES.setControllerArgs)}
                      >
                        Transfer control
                      </Button>
                      <Button
                        variant={"solid"}
                        colorScheme={"orange"}
                        w={["100%", "45%", "initial"]}
                        onClick={() => setState(STATES.withrawFundsArgs)}
                        isDisabled={
                          Number(
                            terminus.terminusPaymentTokenCache.data
                              ?.spenderBalance
                          ) === 0
                        }
                      >
                        Withraw payments
                      </Button>
                      <Button
                        variant={"solid"}
                        colorScheme={"orange"}
                        w={["100%", "45%", "initial"]}
                        onClick={() => setState(STATES.setPoolBasePriceArgs)}
                      >
                        Set pool price
                      </Button>
                      <Button
                        variant={"solid"}
                        colorScheme={"orange"}
                        w={["100%", "45%", "initial"]}
                        onClick={() => setState(STATES.URIArgs)}
                      >
                        Set contract URI
                      </Button>
                      <Button
                        variant={"solid"}
                        colorScheme={"orange"}
                        w={["100%", "45%", "initial"]}
                        onClick={() => setState(STATES.setPaymentTokenArgs)}
                      >
                        Set payment token
                      </Button>
                    </Flex>
                  </Fade>
                )}
                {state === STATES.setControllerArgs && (
                  <Fade in={state === STATES.setControllerArgs ? true : false}>
                    <Flex
                      w="100%"
                      justifyContent="center"
                      px={0}
                      alignItems="baseline"
                      direction="column"
                    >
                      <Input
                        value={address}
                        onChange={handleAddressFieldChange}
                        placeholder="New terminus controller address"
                        size="md"
                        maxW="420px"
                        fontSize={"sm"}
                        isDisabled={terminus.setTerminusController.isLoading}
                      />
                      <Flex alignSelf="center" mt={2}>
                        <Button
                          variant={"solid"}
                          colorScheme={"orange"}
                          onClick={() =>
                            terminus.setTerminusController.mutate({
                              newController: address,
                            })
                          }
                          isLoading={terminus.setTerminusController.isLoading}
                        >
                          Submit
                        </Button>
                        <Button
                          variant={"solid"}
                          colorScheme={"orange"}
                          onClick={() => setState(STATES.buttons)}
                        >
                          Cancel
                        </Button>
                      </Flex>
                    </Flex>
                  </Fade>
                )}
                {state === STATES.setPaymentTokenArgs && (
                  <Fade
                    in={state === STATES.setPaymentTokenArgs ? true : false}
                  >
                    <Flex
                      w="100%"
                      justifyContent="center"
                      px={0}
                      alignItems="baseline"
                      direction={"column"}
                    >
                      <Input
                        value={address}
                        onChange={handleAddressFieldChange}
                        placeholder="New terminus payment token"
                        size="md"
                        maxW="420px"
                        fontSize={"sm"}
                        isDisabled={terminus.setPaymentToken.isLoading}
                      />
                      <Flex alignSelf="center" mt={2}>
                        <Button
                          variant={"solid"}
                          colorScheme={"orange"}
                          onClick={() =>
                            terminus.setPaymentToken
                              .mutateAsync({
                                paymentTokenAddress: address,
                              })
                              .then(() => {
                                setAddressField("");
                                setState(STATES.buttons);
                              })
                          }
                          isLoading={terminus.setTerminusController.isLoading}
                        >
                          Submit
                        </Button>
                        <Button
                          variant={"solid"}
                          colorScheme={"orange"}
                          onClick={() => setState(STATES.buttons)}
                        >
                          Cancel
                        </Button>
                      </Flex>
                    </Flex>
                  </Fade>
                )}
                {state === STATES.withrawFundsArgs && (
                  <Fade in={state === STATES.withrawFundsArgs ? true : false}>
                    <Flex
                      w="100%"
                      justifyContent="center"
                      px={20}
                      alignItems="center"
                      direction={"column"}
                    >
                      <Flex bgColor={"gray.300"} borderRadius="md" p={1}>
                        <NumberInput
                          defaultValue={0}
                          precision={1}
                          step={1}
                          onChange={handleAmountFieldChange}
                          value={amount}
                          size="md"
                          mx={2}
                          isDisabled={terminus.withrawPayments.isLoading}
                        >
                          <NumberInputField />
                          <NumberInputStepper>
                            <NumberIncrementStepper />
                            <NumberDecrementStepper />
                          </NumberInputStepper>
                        </NumberInput>
                        <Slider
                          isDisabled={
                            terminus.withrawPayments.isLoading &&
                            Number(
                              terminus.terminusPaymentTokenCache.data
                                ?.spenderBalance
                            ) > 0
                          }
                          minW="300px"
                          mx={3}
                          flex="1"
                          focusThumbOnChange={false}
                          value={amount}
                          onChange={handleAmountFieldChange}
                          min={0}
                          max={
                            terminus.terminusPaymentTokenCache.data
                              ?.spenderBalance
                              ? Number(
                                  web3Provider.web3.utils.fromWei(
                                    terminus.terminusPaymentTokenCache.data
                                      .spenderBalance,
                                    "ether"
                                  )
                                ) ?? 0
                              : 0
                          }
                        >
                          <SliderTrack>
                            <SliderFilledTrack />
                          </SliderTrack>
                          <SliderThumb fontSize="sm" boxSize="16px" />
                        </Slider>
                      </Flex>
                      <Flex alignSelf={"center"}>
                        <Button
                          variant={"solid"}
                          colorScheme={"orange"}
                          onClick={() =>
                            terminus.withrawPayments
                              .mutateAsync({
                                toAddress: web3Provider.account,
                                amount: web3Provider.web3.utils.toWei(
                                  String(amount),
                                  "ether"
                                ),
                              })
                              .then(() => {
                                setState(STATES.buttons);
                                setAmountField(0);
                              })
                          }
                          isLoading={terminus.withrawPayments.isLoading}
                        >
                          Submit
                        </Button>
                        <Button
                          variant={"solid"}
                          colorScheme={"orange"}
                          onClick={() => setState(STATES.buttons)}
                        >
                          Cancel
                        </Button>
                      </Flex>
                    </Flex>
                  </Fade>
                )}
                {state === STATES.setPoolBasePriceArgs && (
                  <Fade
                    in={state === STATES.setPoolBasePriceArgs ? true : false}
                  >
                    <Flex
                      w="100%"
                      justifyContent="center"
                      px={0}
                      alignItems="center"
                      direction={"column"}
                    >
                      <Flex
                        bgColor={"blue.300"}
                        borderRadius="md"
                        p={1}
                        pb={2}
                        alignItems="center"
                        w="100%"
                        direction={"column"}
                      >
                        New pool base price:
                        <NumberInput
                          defaultValue={0}
                          precision={1}
                          step={1}
                          onChange={handleAmountFieldChange}
                          value={amount}
                          size="md"
                          mx={2}
                          isDisabled={terminus.withrawPayments.isLoading}
                        >
                          <NumberInputField />
                          <NumberInputStepper>
                            <NumberIncrementStepper />
                            <NumberDecrementStepper />
                          </NumberInputStepper>
                        </NumberInput>
                      </Flex>
                      <Flex alignSelf={"center"} mt={2}>
                        <Button
                          variant={"solid"}
                          colorScheme={"orange"}
                          onClick={() =>
                            terminus.setPoolBasePrice
                              .mutateAsync({
                                newPoolBasePrice: web3Provider.web3.utils.toWei(
                                  String(amount),
                                  "ether"
                                ),
                              })
                              .then(() => {
                                setState(STATES.buttons);
                                setAmountField(0);
                              })
                          }
                          isLoading={terminus.withrawPayments.isLoading}
                        >
                          Submit
                        </Button>
                        <Button
                          variant={"solid"}
                          colorScheme={"orange"}
                          onClick={() => setState(STATES.buttons)}
                        >
                          Cancel
                        </Button>
                      </Flex>
                    </Flex>
                  </Fade>
                )}
                {state === STATES.newPoolArgs && (
                  <Fade in={state === STATES.newPoolArgs ? true : false}>
                    <Flex
                      w="100%"
                      justifyContent="center"
                      px={0}
                      alignItems="center"
                      direction="column"
                    >
                      <Flex
                        bgColor={"blue.300"}
                        borderRadius="md"
                        p={1}
                        pb={2}
                        alignItems="center"
                        w="100%"
                        direction={"column"}
                      >
                        New pool maximum supply:
                        <NumberInput
                          onChange={handleAmountFieldChange}
                          value={amount}
                          size="md"
                          mx={2}
                          isDisabled={terminus.createPoolMutation.isLoading}
                        >
                          <NumberInputField />
                          <NumberInputStepper>
                            <NumberIncrementStepper />
                            <NumberDecrementStepper />
                          </NumberInputStepper>
                        </NumberInput>
                      </Flex>
                      <Flex alignSelf="center" mt={2}>
                        <Button
                          variant={"solid"}
                          colorScheme={"orange"}
                          onClick={() =>
                            terminus.createPoolMutation
                              .mutateAsync(String(amount))
                              .then(() => {
                                setState(STATES.buttons);
                                setAmountField(0);
                              })
                          }
                          isLoading={terminus.createPoolMutation.isLoading}
                        >
                          Submit
                        </Button>
                        <Button
                          variant={"solid"}
                          colorScheme={"orange"}
                          onClick={() => {
                            setState(STATES.buttons);
                            setAmountField(0);
                          }}
                        >
                          Cancel
                        </Button>
                      </Flex>
                    </Flex>
                  </Fade>
                )}
                {state === STATES.URIArgs && (
                  <Fade in={state === STATES.URIArgs ? true : false}>
                    <Flex
                      w="100%"
                      justifyContent="center"
                      px={0}
                      alignItems="center"
                      direction={"column"}
                    >
                      <Flex
                        bgColor={"gray.300"}
                        borderRadius="md"
                        p={1}
                        alignItems="center"
                        w="100%"
                      >
                        <Input
                          value={newURI}
                          onChange={handleURIFieldChange}
                          placeholder="New terminus uri"
                          size="md"
                          minW="100%"
                          fontSize={"sm"}
                          isDisabled={terminus.setTerminusController.isLoading}
                        />
                      </Flex>
                      <Flex alignSelf="center">
                        <Button
                          variant={"solid"}
                          colorScheme={"orange"}
                          onClick={() =>
                            terminus.setURI
                              .mutateAsync({ newURI: newURI })
                              .then(() => {
                                setState(STATES.buttons);
                                setNewURI("");
                              })
                          }
                          isLoading={terminus.withrawPayments.isLoading}
                        >
                          Submit
                        </Button>
                        <Button
                          variant={"solid"}
                          colorScheme={"orange"}
                          onClick={() => setState(STATES.buttons)}
                        >
                          Cancel
                        </Button>
                      </Flex>
                    </Flex>
                  </Fade>
                )}
              </>
            </AccordionPanel>
          </AccordionItem>
        </Accordion>
      )}
    </>
  );
};
export default chakra(TerminusControllerPanel, {
  baseStyle: {
    w: "100%",
    direction: ["column", "row"],
    bgColor: "orange.100",
  },
});
