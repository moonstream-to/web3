import React, { useContext } from "react";
import Web3MethodForm from "moonstream-components/src/components/Web3MethodForm";
import { Flex, Text, Center } from "@chakra-ui/react";
import NewDrop from "moonstream-components/src/components/NewDrop";
import { getMethodsABI } from "moonstream-components/src/core/providers/Web3Provider";
import { Dropper } from "../../../../../types/contracts/Dropper";
import { useRouter } from "moonstream-components/src/core/hooks";
const abi = require("../../../../../abi/Dropper.json");
const NewDropPage = () => {
  const router = useRouter();
  if (!router.query["contractAddress"])
    return (
      <Text textColor="white.100"> Contract address must be specified </Text>
    );
  return (
    <Flex className="NewDropPage" w="100%">
      {/* <NewDrop /> */}
      <Center w="100%">
        <Web3MethodForm
          w="100%"
          key={`cp-Web3MethodForm-with`}
          maxW="660px"
          // onSuccess={() => terminus.contractState.refetch()}
          rendered={true}
          hide={["data"]}
          method={getMethodsABI<Dropper["methods"]>(abi, "createClaim")}
          contractAddress={router.query["contractAddress"]}
        />
      </Center>
    </Flex>
  );
};
export default NewDropPage;
