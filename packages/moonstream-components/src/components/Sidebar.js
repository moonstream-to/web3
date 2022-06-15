import {
  ProSidebar,
  Menu,
  SidebarHeader,
  SidebarFooter,
  SidebarContent,
} from "react-pro-sidebar";
import { useContext } from "react";
import RouterLink from "next/link";
import {
  Flex,
  Image,
  IconButton,
  Divider,
  Text,
  Badge,
  Skeleton,
} from "@chakra-ui/react";
import UIContext from "../core/providers/UIProvider/context";
import React from "react";
import { HamburgerIcon, ArrowLeftIcon, ArrowRightIcon } from "@chakra-ui/icons";
import moment from "moment";
import Web3Context from "../core/providers/Web3Provider/context";
import MoonstreamContext from "../core/providers/MoonstreamProvider/context";
import ChainSelector from "./ChainSelector";

const Sidebar = () => {
  const ui = useContext(UIContext);
  const { WHITE_LOGO_W_TEXT_URL, COPYRIGHT_NAME } =
    useContext(MoonstreamContext);
  const web3Provider = useContext(Web3Context);
  return (
    <ProSidebar
      width="240px"
      breakPoint="lg"
      toggled={ui.sidebarToggled}
      onToggle={ui.setSidebarToggled}
      collapsed={ui.sidebarCollapsed}
      hidden={!ui.sidebarVisible}
    >
      <SidebarHeader>
        <Flex>
          <IconButton
            ml={4}
            justifySelf="flex-start"
            colorScheme="blue"
            aria-label="App navigation"
            icon={
              ui.isMobileView ? (
                <HamburgerIcon />
              ) : ui.sidebarCollapsed ? (
                <ArrowRightIcon />
              ) : (
                <ArrowLeftIcon />
              )
            }
            onClick={() => {
              ui.isMobileView
                ? ui.setSidebarToggled(!ui.sidebarToggled)
                : ui.setSidebarCollapsed(!ui.sidebarCollapsed);
            }}
          />
          <RouterLink href="/" passHref>
            <Image
              // h="full"
              // maxH="100%"
              maxW="120px"
              py="0.75rem"
              pl={5}
              src={WHITE_LOGO_W_TEXT_URL}
              alt="Logo"
            />
          </RouterLink>
        </Flex>
      </SidebarHeader>
      <SidebarContent>
        <Divider borderColor="blue.600" />
        <Menu iconShape="square">
          <ChainSelector />
          {/* Not authenticated part of sidebar menu */}

          {web3Provider.buttonText === web3Provider.WALLET_STATES.CONNECTED && (
            <Flex direction="column" px={2} w="100%">
              <Badge
                colorScheme={"pink"}
                variant={"subtle"}
                size="sm"
                borderRadius={"md"}
                m={2}
                p={0}
                whiteSpace="break-spaces"
              ></Badge>
              <Badge
                colorScheme={"blue"}
                variant={"subtle"}
                size="sm"
                borderRadius={"md"}
                m={2}
                p={0}
                whiteSpace="break-spaces"
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

          <Divider
            colorScheme="blue"
            bgColor="gray.300"
            color="blue.700"
            borderColor="blue.700"
          />
        </Menu>
      </SidebarContent>

      <SidebarFooter style={{ paddingBottom: "3rem" }}>
        <Divider color="gray.300" w="100%" />
        <Menu iconShape="square">
          <Divider />
          <Text pt={4} fontSize={"sm"} textColor="gray.700" textAlign="center">
            © {moment().year()} {COPYRIGHT_NAME}
          </Text>
        </Menu>
      </SidebarFooter>
    </ProSidebar>
  );
};

export default Sidebar;
