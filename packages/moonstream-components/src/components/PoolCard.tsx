import React, { FC, useContext } from "react";
import {
  Flex,
  Badge,
  Button,
  chakra,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Text,
} from "@chakra-ui/react";
import { TERMINUS_DIAMOND_ADDRESS } from "../AppDefintions";
import { targetChain } from "../core/providers/Web3Provider";
import { FlexProps } from "@chakra-ui/react";
import RouteButton from "../components/RouteButton";
import useTerminusPool from "../core/hooks/useTerminusPool";
import UIContext from "../core/providers/UIProvider/context";
import Web3MethodForm from "./Web3MethodForm";

// intersecting
interface PoolCardProps extends FlexProps {
  poolId: string;
  hideOpen: boolean;
}

const STATES = {
  default: 0,
  URIArgs: 1,
  mintArgs: 2,
  poolControllerArgs: 3,
};
const PoolCard: FC<PoolCardProps> = ({ poolId, hideOpen, ...props }) => {
  const [state, setState] = React.useState(STATES.default);
  const ui = useContext(UIContext);
  const terminusPool = useTerminusPool({
    DiamondAddress: TERMINUS_DIAMOND_ADDRESS,
    poolId,
    targetChain,
  });

  const PoolBadge = () => (
    <Badge
      colorScheme={"blue"}
      variant="subtle"
      fontSize={["smaller", "small", "md", null, "md"]}
      // size="lg"
      mx={2}
      placeSelf="flex-start"
    >
      Pool ID: #{poolId}
    </Badge>
  );

  return (
    <Flex {...props} px={[2, "20px", "40px"]}>
      <Accordion
        defaultIndex={ui.isMobileView ? undefined : [0]}
        allowToggle={ui.isMobileView ? true : false}
        w="100%"
      >
        <AccordionItem w="100%" borderTop="0" borderBottom="0">
          <h2>
            <AccordionButton>
              <Flex w="100%">
                <PoolBadge />
                <Badge
                  colorScheme={"orange"}
                  variant="outline"
                  fontSize={["smaller", "small", "md", null, "md"]}
                  // size="lg"
                  mx={2}
                  placeSelf="flex-start"
                >
                  Capacity: {terminusPool.terminusPoolCache.data?.supply} /{" "}
                  {terminusPool.terminusPoolCache.data?.capacity}
                </Badge>
              </Flex>
              {ui.isMobileView && <AccordionIcon />}
            </AccordionButton>
          </h2>
          {state === STATES.default && (
            <>
              <AccordionPanel>
                <Text>URI: {terminusPool.terminusPoolCache?.data?.uri}</Text>
                <Flex
                  direction={["column", "row", null, "row"]}
                  flexWrap="wrap"
                  alignItems={"center"}
                  justifyContent="space-between"
                >
                  <Button
                    colorScheme={"blue"}
                    variant="solid"
                    size="sm"
                    w={["100%", "45%", "initial"]}
                    onClick={() => setState(STATES.URIArgs)}
                  >
                    Set URI
                  </Button>
                  <Button
                    colorScheme={"blue"}
                    variant="solid"
                    size="sm"
                    w={["100%", "45%", "initial"]}
                    onClick={() => setState(STATES.mintArgs)}
                  >
                    Mint new
                  </Button>
                  <Button
                    colorScheme={"blue"}
                    variant="solid"
                    size="sm"
                    w={["100%", "45%", "initial"]}
                    onClick={() => setState(STATES.poolControllerArgs)}
                  >
                    Transfer controller
                  </Button>
                  {!hideOpen && (
                    <RouteButton
                      variant="outline"
                      colorScheme="green"
                      size="sm"
                      py={1}
                      w={["100%", "45%", "initial"]}
                      href={`/${poolId}`}
                    >
                      Open
                    </RouteButton>
                  )}
                </Flex>
              </AccordionPanel>
            </>
          )}
          <Web3MethodForm
            key={"method-form-uriargs"}
            rendered={state === STATES.URIArgs ? true : false}
            method={terminusPool.getMethodsABI("setURI")}
            argumentFields={{
              poolURI: {
                placeholder: "New terminus pool uri",
                initialValue: "",
              },
            }}
            callbackFn={terminusPool.setPoolURI.mutateAsync}
            onClick={async (args: any) => {
              terminusPool.setPoolURI.mutateAsync(args).then(() => {
                setState(STATES.default);
              });
            }}
            onCancel={() => setState(STATES.default)}
            isLoading={terminusPool.setPoolURI.isLoading}
          />
          <Web3MethodForm
            key={"method-form-controllerargs"}
            rendered={state === STATES.poolControllerArgs ? true : false}
            method={terminusPool.getMethodsABI("setPoolController")}
            argumentFields={{
              newController: {
                placeholder: "New terminus pool controller address",
              },
            }}
            onClick={async (args: any) => {
              terminusPool.setPoolController.mutateAsync(args).then(() => {
                setState(STATES.default);
              });
            }}
            isLoading={terminusPool.setPoolController.isLoading}
            onCancel={() => setState(STATES.default)}
          />
          <Web3MethodForm
            key={"method-form-mintnew"}
            rendered={state === STATES.mintArgs ? true : false}
            method={terminusPool.getMethodsABI("mint")}
            argumentFields={{
              to: {
                placeholder: "Receiver",
              },
              amount: {
                placeholder: "amount",
              },
            }}
            onClick={async (args: any) => {
              terminusPool.mintPoolNFTMutation.mutateAsync(args).then(() => {
                setState(STATES.default);
              });
            }}
            isLoading={terminusPool.setPoolController.isLoading}
            onCancel={() => setState(STATES.default)}
          />
        </AccordionItem>
      </Accordion>
    </Flex>
  );
};
export default chakra(PoolCard, {
  baseStyle: {
    w: "100%",
    h: "auto",
    borderRadius: "lg",
    my: 2,
    maxW: "1337px",
    py: 2,
    alignItems: "baseline",
    placeContent: "space-between",
    // flexWrap: "wrap",
  },
});
