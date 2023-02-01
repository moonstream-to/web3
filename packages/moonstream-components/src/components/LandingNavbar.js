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
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Portal,
} from "@chakra-ui/react";
import { ChevronDownIcon, HamburgerIcon } from "@chakra-ui/icons";
import UIContext from "../core/providers/UIProvider/context";
import RouteButton from "./RouteButton";
import router from "next/router";
import Web3Context from "../core/providers/Web3Provider/context";
import MoonstreamContext from "../core/providers/MoonstreamProvider/context";
import ChainSelector from "./ChainSelector";

const LandingNavbar = () => {
  const { SITEMAP, PRIMARY_MOON_LOGO_URL } = useContext(MoonstreamContext);
  const ui = useContext(UIContext);
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
        py={1}
        w="160px"
        // flexGrow={1}
        id="Logo Container"
      >
        <RouterLink href="/" passHref>
          <Link
            as={Image}
            w="fit-content"
            h="auto"
            justifyContent="left"
            src={PRIMARY_MOON_LOGO_URL}
            alt="Logo"
          />
        </RouterLink>
      </Flex>

      {!ui.isMobileView && (
        <Flex pr={14} justifyItems="flex-end" flexGrow={1} alignItems="center">
          <Spacer />
          <ButtonGroup variant="solid" spacing={4} pr={16}>
            {SITEMAP.map((item, idx) => {
              return (
                <React.Fragment key={`Fragment-${idx}`}>
                  {!item.children && (
                    <RouteButton
                      key={`${idx}-${item.title}-landing-all-links`}
                      variant="link"
                      href={item.path}
                      color="white"
                      isActive={!!(router.pathname === item.path)}
                    >
                      {item.title}
                    </RouteButton>
                  )}
                  {item.children && (
                    <Menu>
                      <MenuButton
                        as={Button}
                        rightIcon={<ChevronDownIcon />}
                        color="white"
                        variant="link"
                      >
                        {item.title}
                      </MenuButton>
                      <Portal>
                        <MenuList zIndex={100}>
                          {item.children.map((child, idx) => (
                            <RouterLink
                              shallow={true}
                              key={`${idx}-${item.title}-menu-links`}
                              href={child.path}
                              passHref
                            >
                              <MenuItem key={`menu-${idx}`} as={"a"} m={0}>
                                {child.title}
                              </MenuItem>
                            </RouterLink>
                          ))}
                        </MenuList>
                      </Portal>
                    </Menu>
                  )}
                </React.Fragment>
              );
            })}
          </ButtonGroup>
          {web3Provider.buttonText !== web3Provider.WALLET_STATES.CONNECTED && (
            <Button
              isDisabled={
                web3Provider.WALLET_STATES.UNKNOWN_CHAIN ===
                web3Provider.buttonText
              }
              colorScheme={
                web3Provider.buttonText === web3Provider.WALLET_STATES.CONNECTED
                  ? "green"
                  : web3Provider.WALLET_STATES.UNKNOWN_CHAIN ===
                    web3Provider.buttonText
                  ? "red"
                  : "green"
              }
              onClick={web3Provider.onConnectWalletClick}
            >
              {web3Provider.buttonText}
              {"  "}
              <Image
                pl={2}
                h="24px"
                src="https://s3.amazonaws.com/static.simiotics.com/metamask/metamask-fox.svg"
              />
            </Button>
          )}

          {web3Provider.buttonText === web3Provider.WALLET_STATES.CONNECTED && (
            <Flex>
              <code>
                <Badge
                  colorScheme={"blue"}
                  variant={"subtle"}
                  size="md"
                  fontSize="16px"
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
              </code>
            </Flex>
          )}
          <ChainSelector />
        </Flex>
      )}
    </>
  );
};

export default LandingNavbar;
