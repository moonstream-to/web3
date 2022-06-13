import React, { useContext } from "react";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
import {
  Flex,
  Editable,
  EditablePreview,
  EditableInput,
  Center,
} from "@chakra-ui/react";
import PixelsCard from "moonstream-components/src/components/PixelsCard";
import Web3 from "web3";
import { useRouter, useToast } from "moonstream-components/src/core/hooks";
import { useDrops } from "moonstream-components/src/core/hooks/dropper";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
import Dropper from "moonstream-components/src/components/Dropper/Dropper";

const DropperPage = () => {
  const web3 = new Web3();
  const toast = useToast();
  const router = useRouter();

  const web3ctx = useContext(Web3Context);

  const { dropperContracts } = useDrops({
    ctx: web3ctx,
  });

  return (
    <Flex direction={"column"} justifyContent="flex-start" minH="100vh">
      <Editable
        selectAllOnFocus={true}
        submitOnBlur={false}
        bgColor={"blue.700"}
        size="sm"
        fontSize={"sm"}
        textColor="gray.500"
        w="100%"
        minW={["300px", "300px", "360px", "420px", null]}
        variant={"outline"}
        placeholder={
          router.query["contractAddress"] ?? "Dropper contract address"
        }
        defaultValue={router.query["contractAddress"]}
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
        {router.query["contractAddress"] && (
          <Dropper contractAddress={router.query["contractAddress"]} />
        )}
        {!router.query["contractAddress"] && (
          <Center>
            <Flex flexWrap={"wrap"}>
              {dropperContracts.data?.map((contract) => {
                return (
                  <PixelsCard
                    bgColor={"red.900"}
                    w="300px"
                    h="220px"
                    placeContent={"center"}
                    p={4}
                    key={`${contract.address}-dropper`}
                    link={`/dropper/?contractAddress=${contract.address}`}
                    heading={`${contract.title}`}
                    //   imageUrl={assets["lender"]}
                    textColor={"white.100"}
                    level="h2"
                  />
                );
              })}
            </Flex>
          </Center>
        )}
      </Flex>
    </Flex>
  );
};

DropperPage.getLayout = getLayout;
export default DropperPage;
