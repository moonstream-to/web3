import React from "react";
import FeatureCard from "moonstream-components/src/components/FeatureCard";
import { Flex, Center } from "@chakra-ui/react";
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
        <Flex>
          <FeatureCard
            w="300px"
            link="contracts/dropper"
            text=" Set up a loyalty program and reward your players with tokens, items, badges, and achievements"
            heading="dropper"
            //   imageUrl={assets["lender"]}
            alt="Loyalty-Drops"
            textColor={"white.100"}
            level="h2"
          />
          <FeatureCard
            w="300px"
            link="contracts/terminus"
            text="Create lootboxes as rewards for encounters, challenges, and boss fights"
            heading="terminus"
            //   imageUrl={assets["DAO"]}
            alt="Lootboxes"
            textColor={"white.100"}
            level="h2"
            disabled={true}
          />
          <FeatureCard
            w="300px"
            link="contracts/lootbox"
            text="Create on-chain crafting recipes for your blockchain game"
            heading="Lootbox"
            //   imageUrl={assets["NFT"]}
            alt="Crafting"
            textColor={"white.100"}
            level="h2"
            disabled={true}
          />
          <FeatureCard
            w="300px"
            link="contracts/erc20"
            text="Create on-chain crafting recipes for your blockchain game"
            heading="Erc20"
            //   imageUrl={assets["NFT"]}
            alt="erc20"
            textColor={"white.100"}
            level="h2"
            disabled={true}
          />
        </Flex>
      </Center>
    </Flex>
  );
};
export default ContractsList;
