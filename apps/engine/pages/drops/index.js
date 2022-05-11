import React, { useContext } from "react";
import {
  Flex,
  Button,
  Image,
  Center,
  Spinner,
  ScaleFade,
} from "@chakra-ui/react";
import { DEFAULT_METATAGS, AWS_ASSETS_PATH } from "../../src/constants";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
import { targetChain } from "moonstream-components/src/core/providers/Web3Provider";
import useDrops from "moonstream-components/src/core/hooks/useDrops";
import Drop from "moonstream-components/src/components/Dropper/Drop";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
import Paginator from "moonstream-components/src/components/Paginator";
import { useRouter } from "moonstream-components/src/core/hooks";

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

  const { adminClaims, isLoading, uploadFile, pageOptions } = useDrops({
    targetChain: targetChain,
    ctx: web3Provider,
  });

  const router = useRouter();
  React.useEffect(() => {
    router.appendQueries({
      claimsLimit: pageOptions.pageSize,
      claimsPage: pageOptions.page,
    });
    // eslint-disable-next-line
  }, [pageOptions.page, pageOptions.pageSize]);


  if (adminClaims.isLoading)
    return (
      <Flex minH="100vh">
        <Spinner />
      </Flex>
    );

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
          onBack={() => pageOptions.setPage((_currentPage) => _currentPage - 1)}
          onForward={() =>
            pageOptions.setPage((_currentPage) => _currentPage + 1)
          }
          paginatorKey={"claims"}
          setLimit={pageOptions.setLimit}
          hasMore={() => {
            return true;
          }}
        >
          {web3Provider.account &&
            adminClaims?.data?.map((claim, idx) => {
              return (
                <Drop
                  key={`contract-card-${idx}}`}
                  claim={claim}
                  title={claim.title}
                />
              );
            })}
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