import React, { Fragment, useContext } from "react";
import RouterLink from "next/link";
import {
  Button,
  Image,
  ButtonGroup,
  Spacer,
  Link,
  IconButton,
  Flex,
  Badge,
  Skeleton,
} from "@chakra-ui/react";
import { HamburgerIcon } from "@chakra-ui/icons";
import useModals from "../core/hooks/useModals";
import UIContext from "../core/providers/UIProvider/context";
import ChakraAccountIconButton from "./AccountIconButton";
import RouteButton from "./RouteButton";
import {
  ALL_NAV_PATHES,
  APP_ENTRY_POINT,
  IS_AUTHENTICATION_REQUIRED,
  WHITE_LOGO_W_TEXT_URL,
} from "../core/constants";
import router from "next/router";
import { MODAL_TYPES } from "../core/providers/OverlayProvider/constants";
import Web3Context from "../core/providers/Web3Provider/context";
import { targetChain } from "../core/providers/Web3Provider";

const LandingNavbar = () => {
  const ui = useContext(UIContext);
  const { toggleModal } = useModals();
  const web3Provider = useContext(Web3Context);
  return (
    <>
      {ui.isMobileView && (
        <>
          <IconButton
            alignSelf="flex-start"
            colorScheme="blue"
            variant="solid"
            onClick={() => ui.setSidebarToggled(!ui.sidebarToggled)}
            icon={<HamburgerIcon />}
          />
        </>
      )}
      <Flex
        pl={ui.isMobileView ? 2 : 8}
        justifySelf="flex-start"
        h="100%"
        py={1}
        w="200px"
        minW="200px"
        // flexGrow={1}
        id="Logo Container"
      >
        <RouterLink href="/" passHref>
          <Link
            as={Image}
            w="fit-content"
            h="auto"
            justifyContent="left"
            src={WHITE_LOGO_W_TEXT_URL}
            alt="Logo"
          />
        </RouterLink>
      </Flex>

      {!ui.isMobileView && (
        <>
          <Spacer />
          <ButtonGroup variant="solid" spacing={4} pr={16}>
            {web3Provider.buttonText !==
              web3Provider.WALLET_STATES.CONNECTED && (
              <Button
                colorScheme={
                  web3Provider.buttonText ===
                  web3Provider.WALLET_STATES.CONNECTED
                    ? "green"
                    : "green"
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
            )}
            {web3Provider.buttonText ===
              web3Provider.WALLET_STATES.CONNECTED && (
              <Flex>
                <Badge
                  colorScheme={"blue"}
                  variant={"subtle"}
                  size="sm"
                  borderRadius={"md"}
                  mr={2}
                  p={0}
                >
                  <Skeleton
                    isLoaded={web3Provider.account}
                    h="100%"
                    colorScheme={"red"}
                    w="100%"
                    borderRadius={"inherit"}
                    startColor="red.500"
                    endColor="blue.500"
                    p={1}
                  >
                    {web3Provider.account}
                  </Skeleton>
                </Badge>
              </Flex>
            )}
          </ButtonGroup>
          <ButtonGroup variant="link" colorScheme="orange" spacing={4} pr={16}>
            {ALL_NAV_PATHES.map((item, idx) => (
              <RouteButton
                key={`${idx}-${item.title}-landing-all-links`}
                variant="link"
                href={item.path}
                color="white"
                isActive={!!(router.pathname === item.path)}
              >
                {item.title}
              </RouteButton>
            ))}

            {ui.isLoggedIn ||
              (!IS_AUTHENTICATION_REQUIRED && APP_ENTRY_POINT && (
                <RouterLink href={APP_ENTRY_POINT} passHref>
                  <Button
                    as={Link}
                    colorScheme="orange"
                    variant="outline"
                    size="sm"
                    fontWeight="400"
                    borderRadius="2xl"
                  >
                    App
                  </Button>
                </RouterLink>
              ))}
            {!ui.isLoggedIn && IS_AUTHENTICATION_REQUIRED && (
              <Button
                colorScheme="orange"
                variant="solid"
                onClick={() => toggleModal({ type: MODAL_TYPES.SIGNUP })}
                size="sm"
                fontWeight="400"
                borderRadius="2xl"
              >
                Sign Up
              </Button>
            )}
            {!ui.isLoggedIn && IS_AUTHENTICATION_REQUIRED && (
              <Button
                color="white"
                onClick={() => toggleModal({ type: MODAL_TYPES.LOGIN })}
                fontWeight="400"
              >
                Log in
              </Button>
            )}
            {ui.isLoggedIn && IS_AUTHENTICATION_REQUIRED && (
              <ChakraAccountIconButton variant="link" colorScheme="orange" />
            )}
          </ButtonGroup>
        </>
      )}
      {ui.isLoggedIn && IS_AUTHENTICATION_REQUIRED && ui.isMobileView && (
        <>
          <Spacer />
          <ChakraAccountIconButton variant="link" colorScheme="orange" />
        </>
      )}
    </>
  );
};

export default LandingNavbar;
