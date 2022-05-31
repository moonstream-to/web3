import React from "react";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
import {
  Flex,
  Editable,
  EditablePreview,
  EditableInput,
} from "@chakra-ui/react";
import Web3 from "web3";
import Terminus from "moonstream-components/src/components/Terminus";
import { useRouter, useToast } from "moonstream-components/src/core/hooks";

const Whitelists = () => {
  const web3 = new Web3();
  const toast = useToast();
  const router = useRouter();

  return (
    <Flex direction={"column"} justifyContent="flex-start" minH="100vh">
      <Editable
        bgColor={"blue.700"}
        size="sm"
        fontSize={"sm"}
        textColor="gray.500"
        w="100%"
        minW={["300px", "300px", "360px", "420px", null]}
        variant={"outline"}
        placeholder={
          router.query["contractAddress"] ?? "Terminus contract address"
        }
        onSubmit={(nextValue) => {
          if (web3.utils.isAddress(nextValue)) {
            router.appendQuery("contractAddress", nextValue, false, false);
          } else {
            toast("Invalid address", "error");
          }
        }}
      >
        <EditablePreview w="100%" px={2} />
        <EditableInput w="100%" px={2} />
      </Editable>
      <Flex placeSelf={"center"} direction={"row"} flexWrap="wrap" w="100%">
        <Terminus />
      </Flex>
    </Flex>
  );
};

Whitelists.getLayout = getLayout;
export default Whitelists;
