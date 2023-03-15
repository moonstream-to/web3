import React, { useContext } from "react";
import { Flex, Center } from "@chakra-ui/react";
import { DEFAULT_METATAGS, AWS_ASSETS_PATH } from "../src/constants";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
// import { getLayout } from "../src/layouts/AppLayout";
import FeatureCard from "../../../packages/moonstream-components/src/components/FeatureCardPlay";
import { getLayout } from "../../../packages/moonstream-components/src/layoutsForPlay/EngineLayout";

const assets: any = {
  onboarding:
    "https://s3.amazonaws.com/static.simiotics.com/unicorn_bazaar/unim-onboarding.png",
  cryptoTraders: `${AWS_ASSETS_PATH}/crypto+traders.png`,
  smartDevelopers: `${AWS_ASSETS_PATH}/smart+contract+developers.png`,
  lender: `${AWS_ASSETS_PATH}/lender.png`,
  DAO: `${AWS_ASSETS_PATH}/DAO .png`,
  NFT: `${AWS_ASSETS_PATH}/NFT.png`,
};
const Homepage = () => {
  const web3Provider = useContext(Web3Context);

  return (
    <Flex
      w="100%"
      minH="100vh"
      bgColor={"#1A1D22"}
      direction={"column"}
      px="7%"
      mt="100px"
    >
      <Center>
        {web3Provider.account && (
          <Flex>
            <FeatureCard
              w="300px"
              link="/inventory"
              text=" Inventory"
              heading="Inventory"
              imageUrl={assets["lender"]}
              alt="Inventory"
              level="h2"
              // imgH="220px"
              h="450px"
            />
            <FeatureCard
              w="300px"
              link="/drops"
              text="Claim drops that you are eligible "
              heading="Claim drops"
              imageUrl={assets["DAO"]}
              alt="Lootboxes"
              textColor={"white.100"}
              level="h2"
              // imgH="220px"
              h="450px"
            />
            <FeatureCard
              w="300px"
              link="/games"
              text="Games supported by Moonstream."
              heading="Games"
              imageUrl={assets["NFT"]}
              alt="games"
              textColor={"white.100"}
              level="h2"
              h="450px"
              // imgH="220px"
            />
          </Flex>
        )}
      </Center>
    </Flex>
  );
};

interface Preconnect {
  rel: string;
  href: string;
  as?: string;
}

// Homepage.getLayout = getLayout;

export async function getStaticProps() {
  const assetPreload: Array<Preconnect> = assets
    ? Object.keys(assets).map((key) => {
        return {
          rel: "preload",
          href: assets[key],
          as: "image",
        };
      })
    : [];
  const preconnects: Array<Preconnect> = [
    { rel: "preconnect", href: "https://s3.amazonaws.com" },
  ];

  const preloads = assetPreload.concat(preconnects);

  return {
    props: { metaTags: DEFAULT_METATAGS, preloads },
  };
}

Homepage.getLayout = getLayout;
export default Homepage;
