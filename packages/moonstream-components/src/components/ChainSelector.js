import React, { useContext } from "react";

import {
  Menu,
  MenuItem,
  MenuList,
  Image,
  MenuButton,
  Button,
  Icon,
} from "@chakra-ui/react";
import { ChevronDownIcon } from "@chakra-ui/icons";
import { MdOutlineLaptopMac } from "react-icons/md";
import Web3Context from "../core/providers/Web3Provider/context";
const ChainSelector = () => {
  const web3Provider = useContext(Web3Context);
  return (
    <Menu>
      <MenuButton
        h="36px"
        mx={2}
        borderRadius="10px"
        as={Button}
        textDecoration="none"
        _expanded={{
          color: "white",
          fontWeight: "700",
          backgroundColor: "#1A1D22",
        }}
        _active={{ textDecoration: "none", backgroundColor: "#1A1D22" }}
        _focus={{ textDecoration: "none", backgroundColor: "#1A1D22" }}
        _hover={{ textDecoration: "none", fontWeight: "700" }}
        rightIcon={<ChevronDownIcon />}
        leftIcon={
          <Image
            display={"inline"}
            // w="24px"
            h="24px"
            mr={4}
            src={
              web3Provider.targetChain?.name === "ethereum"
                ? "https://s3.amazonaws.com/static.simiotics.com/moonstream/assets/ethereum/eth-diamond-rainbow.png"
                : web3Provider.targetChain?.name === "localhost"
                ? ""
                : "https://s3.amazonaws.com/static.simiotics.com/moonstream/assets/matic-token-inverted-icon.png"
            }
          ></Image>
        }
        color="white"
        variant="outline"
        fontSize="16px"
      >
        {web3Provider.targetChain?.name ?? "Chain selector"}
      </MenuButton>
      <MenuList
        bg="#1A1D22"
        color="white"
        borderRadius="30px"
        border="1px solid white"
      >
        <MenuItem
          fontSize={"16px"}
          _hover={{
            backgroundColor: "transparent",
            color: "#F56646",
            fontWeight: "700",
          }}
          _focus={{
            backgroundColor: "transparent",
            color: "#F56646",
            fontWeight: "700",
          }}
          // isDisabled={web3Provider.targetChain?.name === "ethereum"}
          onClick={() => {
            web3Provider.changeChain("ethereum");
          }}
        >
          <Image
            // w="24px"
            h="24px"
            mr={6}
            src="https://s3.amazonaws.com/static.simiotics.com/moonstream/assets/eth-diamond-rainbow.png"
          ></Image>
          Ethereum
        </MenuItem>
        <MenuItem
          fontSize={"16px"}
          _hover={{
            backgroundColor: "transparent",
            color: "#F56646",
            fontWeight: "700",
          }}
          // isDisabled={web3Provider.targetChain?.name === "polygon"}
          onClick={() => {
            web3Provider.changeChain("polygon");
          }}
        >
          <Image
            // w="24px"
            h="24px"
            mr={4}
            src="https://s3.amazonaws.com/static.simiotics.com/moonstream/assets/matic-token-inverted-icon.png"
          ></Image>
          Polygon
        </MenuItem>
        <MenuItem
          fontSize={"16px"}
          _hover={{
            backgroundColor: "transparent",
            color: "#F56646",
            fontWeight: "700",
          }}
          // isDisabled={web3Provider.targetChain?.name === "mumbai"}
          onClick={() => {
            web3Provider.changeChain("mumbai");
          }}
        >
          <Image
            // w="24px"
            h="24px"
            mr={4}
            src="https://s3.amazonaws.com/static.simiotics.com/moonstream/assets/matic-token-inverted-icon.png"
          ></Image>
          Mumbai
        </MenuItem>
        <MenuItem
          fontSize={"16px"}
          _hover={{
            backgroundColor: "transparent",
            color: "#F56646",
            fontWeight: "700",
          }}
          // isDisabled={web3Provider.targetChain?.name === "localhost"}
          onClick={() => {
            web3Provider.changeChain("localhost");
          }}
        >
          <Icon h="24px" mr={4} as={MdOutlineLaptopMac} />
          Localhost
        </MenuItem>
      </MenuList>
    </Menu>
  );
};
export default ChainSelector;
