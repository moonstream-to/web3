import React, { useContext } from "react";
import {
  Flex,
  Button,
  Image,
  Center,
  Spinner,
  Link,
  ButtonGroup,
} from "@chakra-ui/react";
import { DEFAULT_METATAGS, AWS_ASSETS_PATH } from "../../src/constants";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
import { useRouter } from "moonstream-components/src/core/hooks";
import DropperContract from "moonstream-components/src/components/DropperContract";
import usePlayerClaims from "moonstream-components/src/core/hooks/dropper/useClaims";
import { useDrops } from "moonstream-components/src/core/hooks/dropper";
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

  const router = useRouter();
  const { query } = router;

  const dropper = useDrops({
    ctx: web3Provider,
  });

  const { playerClaims, claimsList } = usePlayerClaims({
    ctx: web3Provider,
  });

  if (
    playerClaims.isLoading ||
    dropper.dropperContracts.isLoading ||
    claimsList.isLoading
  )
    return (
      <Flex minH="100vh">
        <Spinner />
      </Flex>
    );

  return (
    <Flex
      w="100%"
      minH="100vh"
      bgColor={"#1A1D22"}
      direction={"column"}
      px="7%"
    >
      {web3Provider.account &&
        dropper.dropperContracts.data
          ?.filter(
            (contract) =>
              playerClaims.data?.findIndex(
                (claim) => claim.dropper_contract_address === contract.address
              ) !== -1
          )
          .map((contract) => {
            return (
              <DropperContract
                mt="20px"
                borderRadius="20px"
                key={contract.id}
                contractResource={contract}
              >
                <ButtonGroup direction="row" variant={"solid"} mt="10px">
                  <Button
                    as={Link}
                    variant="outline"
                    color="#F56646"
                    borderColor="#F56646"
                    _hover={{
                      color: "#F4532F",
                      borderColor: "#F4532F",
                      backgroundColor: "transparent",
                      textDecoration: "none",
                      fontWeight: "800",
                    }}
                    _active={{
                      color: "#F4532F",
                      borderColor: "#F4532F",
                      backgroundColor: "transparent",
                    }}
                    onClick={() => {
                      if (query?.dropId) {
                        router.push({
                          pathname: "/drops",
                        });
                      } else {
                        router.push({
                          pathname: "drops/details",
                          query: {
                            dropperAddress: contract.address,
                          },
                        });
                      }
                    }}
                  >
                    {query?.dropId ? `Back to list` : `See claims`}
                  </Button>
                  <Button
                    disabled
                    _disabled={{
                      backgroundColor: "#4D4D4D",
                      color: "gray.1100",
                      cursor: "default",
                    }}
                    _focus={{
                      backgroundColor: "#4D4D4D",
                      color: "gray.1100",
                    }}
                    _hover={{
                      backgroundColor: "#4D4D4D",
                      color: "gray.1100",
                    }}
                    _active={{
                      backgroundColor: "#4D4D4D",
                      color: "gray.1100",
                    }}
                  >
                    Claim all at once
                  </Button>
                </ButtonGroup>
              </DropperContract>
            );
          })}

      {!web3Provider.account &&
        web3Provider.buttonText !== web3Provider.WALLET_STATES.CONNECTED && (
          <Center>
            <Button
              mt={20}
              colorScheme={
                web3Provider.buttonText === web3Provider.WALLET_STATES.CONNECTED
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
