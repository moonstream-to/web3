import React, { useContext, useState } from "react";
import {
  Flex,
  FormLabel,
  Spinner,
  NumberInput,
  NumberInputField,
  Button,
  Spacer,
  Text,
  Heading,
  SlideFade,
} from "@chakra-ui/react";
import { getMethodsABI, targetChain } from "../core/providers/Web3Provider";

import { useTerminusContract } from "../core/hooks/useTerminusContract";
import Web3Context from "../core/providers/Web3Provider/context";
import { useRouter } from "../core/hooks";
import TerminusPool from "./TerminusPool";
import TerminusControllerPanel from "./TerminusControllerPanel";
import Paginator from "./Paginator";
import Web3MethodForm from "./Web3MethodForm";
import { MockTerminus } from "../../../../types/contracts/MockTerminus";
import Metadata from "./Metadata";
import useLink from "../core/hooks/useLink";
const terminusABI = require("../../../../abi/MockTerminus.json");
const STATES = {
  mint: 1,
  batchMint: 2,
};
const Terminus = () => {
  const [isOpen, onOpen] = React.useState(false);
  const [state, setState] = React.useState(STATES.mint);
  const [poolToCheck, setPoolToCheck] = useState<number>();
  const [page, setPage] = useState(0);
  const [limit, setLimit] = useState(0);
  const router = useRouter();

  const { contractAddress } = router.query;
  const web3ctx = useContext(Web3Context);

  const terminus = useTerminusContract({
    address: contractAddress,
    targetChain: targetChain,
    ctx: web3ctx,
  });

  const uri = useLink({ link: terminus.contractState.data?.contractURI });
  const handleKeypress = (e: any) => {
    //it triggers by pressing the enter key
    if (e.charCode === 13) {
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    router.push({
      pathname: "/terminus/details",
      query: {
        contractAddress: contractAddress,
        poolId: poolToCheck,
      },
    });
  };

  if (!contractAddress)
    return <Text>{"Please specify terminus address "}</Text>;
  if (terminus.contractState.isLoading || !terminus.contractState.data)
    return <Spinner />;

  return (
    <Flex
      w="100%"
      minH="100vh"
      direction={"column"}
      id="flexid"
      alignSelf={"center"}
    >
      <Flex bgColor="blue.1000" pt={4} px={2} direction="column">
        <Heading as="h2" size="md" borderBottomWidth={"2px"}>
          Contract panel
        </Heading>
        <Flex direction={"row"} bgColor="blue.1000" flexWrap={"wrap"}>
          {uri?.data && (
            <Metadata
              boxShadow={"md"}
              zIndex={11}
              flexGrow={1}
              flexShrink={1}
              flexBasis="150px"
              minW="320px"
              borderRadius="md"
              borderColor={"blue.1200"}
              borderWidth={"3px"}
              p={4}
              m={2}
              h="420px"
              maxW="420px"
              metadata={uri?.data}
            />
          )}
          {terminus.contractState.data.controller === web3ctx.account && (
            <TerminusControllerPanel
              flexBasis={"500px"}
              flexGrow={1}
              borderRadius={"md"}
              my={2}
              bgColor="blue.600"
              py={4}
              direction={["column", "row"]}
              address={contractAddress}
            />
          )}
        </Flex>
      </Flex>
      <Flex
        w="100%"
        direction="column"
        bgColor={"blue.600"}
        placeItems="center"
        my={4}
      >
        <Flex w="100%" p={2} placeItems="center" direction={"row"}>
          <FormLabel size="lg" pt={2}>
            See pool details:
          </FormLabel>
          <NumberInput
            size="sm"
            variant="flushed"
            colorScheme="blue"
            placeholder="Enter pool id"
            onKeyPress={handleKeypress}
            value={poolToCheck}
            onChange={(value: string) => setPoolToCheck(Number(value))}
          >
            <NumberInputField px={2} />
          </NumberInput>
          <Button
            mx={4}
            onClick={() => handleSubmit()}
            size="sm"
            variant={"solid"}
            colorScheme="orange"
          >
            See pool details
          </Button>
          <Spacer />
          <Button
            isActive={state === STATES.batchMint && isOpen}
            key={`batchmint`}
            colorScheme={"orange"}
            size="sm"
            variant={"ghost"}
            onClick={() => {
              if (state === STATES.batchMint) {
                onOpen((current) => !current);
              } else {
                setState(() => STATES.batchMint);
                onOpen(true);
              }
            }}
          >
            Batch mint
          </Button>
        </Flex>
        {state === STATES.batchMint && (
          <SlideFade in={isOpen}>
            <Web3MethodForm
              mb={4}
              w="100%"
              display={isOpen ? "flex" : "none"}
              key={`cp-Web3MethodForm-batchMint`}
              maxW="660px"
              onSuccess={() => terminus.contractState.refetch()}
              argumentFields={{
                data: {
                  placeholder: "",
                  initialValue: web3ctx.web3.utils.utf8ToHex(""),
                },
              }}
              rendered={true}
              BatchInputs={["poolIDs", "amounts"]}
              hide={["data"]}
              method={getMethodsABI<MockTerminus["methods"]>(
                terminusABI,
                "mintBatch"
              )}
              contractAddress={contractAddress}
            />
          </SlideFade>
        )}
      </Flex>
      <Paginator
        setPage={setPage}
        setLimit={setLimit}
        paginatorKey={`pools`}
        hasMore={page * limit < Number(terminus.contractState.data.totalPools)}
        page={page}
        pageSize={limit}
        pageOptions={["5", "10", "25", "50"]}
        my={2}
      >
        {Array.from(
          Array(
            (page + 1) * limit < Number(terminus.contractState.data.totalPools)
              ? limit
              : limit -
                  ((page + 1) * limit -
                    Number(terminus.contractState.data.totalPools))
          ),
          (e, i) => {
            return (
              <TerminusPool
                key={limit * page + i + 1}
                address={contractAddress}
                poolId={(limit * page + i + 1).toString()}
              />
            );
          }
        )}
      </Paginator>
    </Flex>
  );
};

export default Terminus;
