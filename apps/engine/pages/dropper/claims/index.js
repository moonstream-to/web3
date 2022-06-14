import React, { useContext, useState } from "react";
import {
  Flex,
  Button,
  Image,
  Center,
  Spinner,
  ScaleFade,
} from "@chakra-ui/react";
import { DEFAULT_METATAGS, AWS_ASSETS_PATH } from "../../../src/constants";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
import { useDropperContract } from "moonstream-components/src/core/hooks/dropper";
import { useRouter } from "moonstream-components/src/core/hooks";
import Claim from "moonstream-components/src/components/Dropper/Claim";
import Paginator from "moonstream-components/src/components/Paginator";
const assets = {
  onboarding:
    "https://s3.amazonaws.com/static.simiotics.com/unicorn_bazaar/unim-onboarding.png",
  cryptoTraders: `${AWS_ASSETS_PATH}/crypto+traders.png`,
  smartDevelopers: `${AWS_ASSETS_PATH}/smart+contract+developers.png`,
  lender: `${AWS_ASSETS_PATH}/lender.png`,
  DAO: `${AWS_ASSETS_PATH}/DAO .png`,
  NFT: `${AWS_ASSETS_PATH}/NFT.png`,
};

const Drops = () => {
  const web3Provider = useContext(Web3Context);

  const web3ctx = useContext(Web3Context);
  const router = useRouter();
  const { contractAddress } = router.query;

  const [page, setPage] = useState(0);
  const [limit, setLimit] = useState(0);
  const dropper = useDropperContract({
    dropperAddress: contractAddress,
    ctx: web3ctx,
  });

  if (!contractAddress) return "contract address plz";
  if (dropper.contractState.isLoading) return <Spinner />;

  return (
    <ScaleFade in>
      <Flex
        w="100%"
        minH="100vh"
        bgColor={"blue.1200"}
        direction={"column"}
        px="7%"
      >
        <Paginator
          setPage={setPage}
          setLimit={setLimit}
          paginatorKey={`pools`}
          hasMore={page * limit < Number(dropper.contractState.data?.numClaims)}
          page={page}
          pageSize={limit}
          pageOptions={["5", "10", "25", "50"]}
          my={2}
        >
          {Array.from(
            Array(Number(dropper.contractState.data.numClaims)),
            (v, i) => {
              return (
                <Claim
                  key={i}
                  dropperAddress={contractAddress}
                  claimIdx={i}
                ></Claim>
              );
            }
          )}
        </Paginator>

        {!web3Provider.account &&
          web3Provider.buttonText !== web3Provider.WALLET_STATES.CONNECTED && (
            <Center>
              <Button
                mt={20}
                colorScheme={
                  web3Provider.buttonText ===
                  web3Provider.WALLET_STATES.CONNECTED
                    ? "orange"
                    : "orange"
                }
                onClick={web3Provider.onConnectWalletClick}
              >
                {web3Provider.buttonText}
                {"  "}
                <Image
                  pl={2}
                  h="24px"
                  alt={"metamask"}
                  src="https://raw.githubusercontent.com/MetaMask/brand-resources/master/SVG/metamask-fox.svg"
                />
              </Button>
            </Center>
          )}
      </Flex>
    </ScaleFade>
  );
};

export async function getStaticProps() {
  const assetPreload = assets
    ? Object.keys(assets).map((key) => {
        return {
          rel: "preload",
          href: assets[key],
          as: "image",
        };
      })
    : [];
  const preconnects = [{ rel: "preconnect", href: "https://s3.amazonaws.com" }];

  const preloads = assetPreload.concat(preconnects);

  return {
    props: { metaTags: DEFAULT_METATAGS, preloads },
  };
}

Drops.getLayout = getLayout;
export default Drops;
