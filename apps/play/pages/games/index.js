import React from "react";
import { getLayout } from "../../../../packages/moonstream-components/src/layoutsForPlay/EngineLayout";
import { Flex, Center } from "@chakra-ui/react";
import FeatureCard from "moonstream-components/src/components/FeatureCardPlay";
const Games = () => {
  return (
    <Flex className="Games">
      <Flex
        w="100%"
        minH="100vh"
        bgColor={"#1A1D22"}
        direction={"column"}
        mt="100px"
      >
        <Center>
          <Flex wrap="wrap" justifyContent="center">
            <FeatureCard
              w="300px"
              imgH="140px"
              link="games/CryptoUnicorns"
              text="A digital pet collecting and farming game, built on blockchain"
              //   heading="Crypto Unicorns"
              imageUrl={
                "https://s3.amazonaws.com/static.simiotics.com/crypto-unicorns/cu_logo.png"
              }
              alt="Crypto Unicorns"
              textColor={"white.100"}
              level="h2"
              imgPading={24}
              h="450px"
            />
            <FeatureCard
              w="300px"
              isExternal={true}
              link="https://conquest-eth.play.moonstream.to/"
              imgH="140px"
              text="Conquest.eth - An unstoppable and open-ended game of strategy and diplomacy running on the Ethereum Virtual Machine."
              //   heading="Conquest.eth"
              imageUrl={
                "https://s3.amazonaws.com/static.simiotics.com/conquest-eth/conquest_eth.png"
              }
              alt="Crypto Unicorns"
              textColor={"white.100"}
              level="h2"
              imgPading={24}
              //   disabled={true}
              h="450px"
            />
            {/* <video src="https://www.champions.io/static/karkadon-desktop-ee6012464e76b83dc149bd896368048a.mp4"></video> */}
            <FeatureCard
              w="300px"
              imgH="140px"
              link="/games/OpenGamingCollective/"
              text="View your Open Gaming Collective badges."
              imageUrl={
                "https://s3.amazonaws.com/static.simiotics.com/play/games/ogc-logo.png"
              }
              alt="Open Gaming Collective"
              textColor={"white.100"}
              level="h2"
              imgPading={24}
              h="450px"
            />
            <FeatureCard
              w="300px"
              imgH="140px"
              link="games/crypto unicorns"
              text="Ascension is a blockchain game built by Jam City, an award-winning game company led by former MySpace co-founder and CEO Chris DeWolfe"
              //   heading="Champions Ascension"
              imageUrl={
                "https://s3.amazonaws.com/static.simiotics.com/champions-ascension/champions.png"
              }
              alt="Champions Ascension"
              textColor={"white.100"}
              level="h2"
              disabled={true}
              imgPading={24}
              h="450px"
            />
          </Flex>
        </Center>
      </Flex>
    </Flex>
  );
};

Games.getLayout = getLayout;

export default Games;
