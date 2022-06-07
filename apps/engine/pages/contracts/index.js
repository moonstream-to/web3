import React from "react";
import { Flex, Center } from "@chakra-ui/react";
import PixelsCard from "moonstream-components/src/components/PixelsCard";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";

const CONTRACTS = [
  "chainlinkCoordinator",
  "ControllableWithTerminus",
  "dropper",
  "erc20",
  "erc677Receiver",
  "erc721",
  "lootbox",
  "lootboxRandomness",
  "terminus",
  "VRFuser",
];
const ContractsList = () => {
  return (
    <Flex
      className="ContractsList"
      w="100%"
      minH="100vh"
      bgColor={"blue.1200"}
      direction={"column"}
      px="7%"
      mt="100px"
    >
      <Center>
        <Flex flexWrap={"wrap"}>
          {CONTRACTS.map((contract) => {
            return (
              <PixelsCard
                bgColor={"red.900"}
                w="300px"
                p={4}
                key={`${contract}-contracts`}
                link={`contracts/${contract}`}
                heading={`${contract}`}
                //   imageUrl={assets["lender"]}
                textColor={"white.100"}
                level="h2"
              />
            );
          })}
        </Flex>
      </Center>
    </Flex>
  );
};

ContractsList.getLayout = getLayout;
export default ContractsList;
