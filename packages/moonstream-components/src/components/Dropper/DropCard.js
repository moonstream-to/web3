import React, { useContext } from "react";
import {
  chakra,
  Flex,
  Text,
  Stack,
  Heading,
  Spinner,
  Button,
  Skeleton,
} from "@chakra-ui/react";
import useDrop from "../../core/hooks/useDrop";
import Web3Context from "../../core/providers/Web3Provider/context";
import { targetChain } from "../../core/providers/Web3Provider";
import Erc20Card from "../Erc20Card";
import useTerminusPools from "../../core/hooks/useTerminusPools";
const DropCard = ({ drop }) => {
  const web3Provider = useContext(Web3Context);

  // const dropHook = useDrop({
  //   dropperAddress: process.env.NEXT_PUBLIC_DROPPER_ADDRESS ?? "",
  //   targetChain: targetChain,
  //   ctx: web3Provider,
  //   claimId: drop.id,
  // });

  // const terminusPool = useTerminusPools({
  //   terminusAddress: drop.terminus_address,
  //   poolId: drop.terminus_pool_id,
  //   targetChain: targetChain,
  //   ctx: web3Provider,
  // });
  // if (dropHook.isLoadingState || terminusPool.terminusPoolCache.isLoading)
  //   return <Spinner />;

  return (
    <>
      <Flex
        bgColor="blue.600"
        borderRadius="md"
        h="80px"
        px={4}
        py={2}
        flexGrow={1}
        alignContent="baseline"
        justifyContent={"space-between"}
        alignItems="top"
        //   direction={"column"}
      >
        <Flex direction={"column"}>
          <Heading
            fontWeight={600}
            textColor="gray.100"
            h="min-content"
            as="h3"
            fontSize={"md"}
          >
            {drop.title}
          </Heading>
          <chakra.span>{drop.description}</chakra.span>
        </Flex>
        {/* {claimer.state && claimer.state.claim[0] == "20" && (
          <Erc20Card
            isLoading={claimer.isLoadingState}
            address={claimer.state.claim[1]}
            amount={web3Provider.web3.utils.fromWei(
              claimer.state.claim[3],
              "ether"
            )}
          />
        )}*/}
        <Button
        // isDisabled={!claimer.state.canClaim}
        // onClick={() => claimer.claim.mutate()}
        // isLoading={claimer.isLoadingClaim}
        // colorScheme={"orange"}
        >
          Activate
        </Button>
        <Button
        // isDisabled={!claimer.state.canClaim}
        // onClick={() => claimer.claim.mutate()}
        // isLoading={claimer.isLoadingClaim}
        // colorScheme={"orange"}
        >
          Deactivate
        </Button>
        <Button
        // isDisabled={!claimer.state.canClaim}
        // onClick={() => claimer.claim.mutate()}
        // isLoading={claimer.isLoadingClaim}
        // colorScheme={"orange"}
        >
          Upload whitelist
        </Button>
      </Flex>
    </>
  );
};

export default DropCard;
