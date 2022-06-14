import {
  chakra,
  Flex,
  Editable as _Editable,
  EditablePreview,
  EditableInput,
} from "@chakra-ui/react";
import React from "react";
import Web3 from "web3";
import { AbiItem } from "web3-utils";
import { useToast } from "../core/hooks";
import Web3MethodForm from "./Web3MethodForm";

const _ContractInterface = ({
  abi,
  initalContractAddress,
  ...props
}: {
  abi: AbiItem[];
  initalContractAddress?: string;
}) => {
  const toast = useToast();
  const [contractAddress, setContractAddress] = React.useState(
    initalContractAddress
  );
  const web3 = new Web3();

  return (
    <Flex
      direction={"column"}
      {...props}
      justifyContent="flex-start"
      minH="100vh"
    >
      <_Editable
        bgColor={"blue.700"}
        size="sm"
        fontSize={"sm"}
        textColor="gray.500"
        w="100%"
        minW={["300px", "300px", "360px", "420px", null]}
        variant={"outline"}
        defaultValue={initalContractAddress}
        placeholder="Contract address"
        onSubmit={(nextValue: any) => {
          if (web3.utils.isAddress(nextValue)) {
            setContractAddress(nextValue);
          } else {
            toast("not a checksum address", "error");
          }
        }}
      >
        <EditablePreview w="100%" px={2} />
        <EditableInput w="100%" px={2} />
      </_Editable>
      <Flex
        placeSelf={"center"}
        direction={"row"}
        flexWrap="wrap"
        // justifyItems={"center"}
        justifyContent={"center"}
      >
        {contractAddress &&
          abi
            .filter(
              (element: any) =>
                element.type === "function" &&
                element.stateMutability !== "view"
            )
            .map((element: any, idx: any) => {
              return (
                <Web3MethodForm
                  w="320px"
                  key={`Web3MethodForm-${idx}`}
                  contractAddress={contractAddress}
                  m={5}
                  p={5}
                  maxW="420px"
                  bgColor={"blue.300"}
                  boxShadow="md"
                  method={element}
                  rendered={true}
                  flexDirection="column"
                />
              );
            })}
      </Flex>
    </Flex>
  );
};

const ContractInterface = chakra(_ContractInterface);

export default ContractInterface;
