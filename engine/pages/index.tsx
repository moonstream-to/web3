import React, { useContext } from "react";
import { Flex, Center } from "@chakra-ui/react";
import { DEFAULT_METATAGS, AWS_ASSETS_PATH } from "../src/constants";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
// import { getLayout } from "../src/layouts/AppLayout";
import FeatureCard from "../../packages/moonstream-components/src/components/FeatureCard";

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
      bgColor={"blue.1200"}
      direction={"column"}
      px="7%"
      mt="100px"
    >
      <Center>
        {web3Provider.account && (
          <Flex>
            <FeatureCard
              w="300px"
              link="/drops"
              text="Create new whitelist with loaylty rewards"
              heading="Drops"
              imageUrl={assets["cryptoTraders"]}
              alt="Drops"
              textColor={"white.100"}
              level="h2"
            />
            <FeatureCard
              w="300px"
              link="/drops"
              text="Create new whitelist with loaylty rewards"
              heading="Guards"
              imageUrl={assets["DAO"]}
              alt="Drops"
              textColor={"white.100"}
              level="h2"
              disabled={true}
            />
            <FeatureCard
              w="300px"
              link="/drops"
              text="Create new whitelist with loaylty rewards"
              heading="Treasury"
              imageUrl={assets["NFT"]}
              alt="Drops"
              textColor={"white.100"}
              level="h2"
              disabled={true}
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

export default Homepage;
