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
    <code>
      <Menu>
        <MenuButton
          mx={2}
          as={Button}
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
          // color="white"
          colorScheme="orange"
          variant="outline"
          fontSize={"24px"}
        >
          {web3Provider.targetChain?.name ?? "Chain selector"}
        </MenuButton>
        <MenuList>
          <MenuItem
            fontSize={"24px"}
            isDisabled={web3Provider.targetChain?.name === "ethereum"}
            onClick={() => {
              web3Provider.changeChain("ethereum");
            }}
          >
            <Image
              // w="24px"
              h="24px"
              mr={6}
              src="https://s3.amazonaws.com/static.simiotics.com/moonstream/assets/eth-diamond-black.png"
            ></Image>
            Ethereum
          </MenuItem>
          <MenuItem
            fontSize={"24px"}
            isDisabled={web3Provider.targetChain?.name === "polygon"}
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
            fontSize={"24px"}
            isDisabled={web3Provider.targetChain?.name === "mumbai"}
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
            fontSize={"24px"}
            isDisabled={web3Provider.targetChain?.name === "localhost"}
            onClick={() => {
              web3Provider.changeChain("localhost");
            }}
          >
            <Icon h="24px" mr={4} as={MdOutlineLaptopMac} />
            Localhost
          </MenuItem>
        </MenuList>
      </Menu>
    </code>
  );
};
export default ChainSelector;
