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
    <Menu variant="bw" placement="bottom-end">
      <MenuButton
        h="36px"
        mx={2}
        as={Button}
        variant="bwOutline"
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
      >
        {web3Provider.targetChain?.name ?? "Chain selector"}
      </MenuButton>
      <MenuList minW="0">
        <MenuItem
          isDisabled={web3Provider.targetChain?.name === "ethereum"}
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
  );
};
export default ChainSelector;
