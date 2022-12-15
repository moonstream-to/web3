import { Text, Icon, Image, Link, Box, Flex } from "@chakra-ui/react";
import { FiExternalLink } from "react-icons/fi";
import { SHADOWCORN_CONTRACT_ADDRESS } from "moonstream-components/src/core/cu/constants";

const buildOpenseaLink = (tokenId) => {
  return `https://opensea.io/assets/matic/${SHADOWCORN_CONTRACT_ADDRESS}/${tokenId}`;
};

const ShadowcornRow = ({ shadowcorn, tokenId }) => {
  return (
    <Link
      p="0px"
      _hover={{ bgColor: "#454545" }}
      href={buildOpenseaLink(tokenId)}
      isExternal
    >
      <Flex alignItems="center">
        {shadowcorn && (
          <Image
            alt="sc"
            src={shadowcorn.image}
            w={["16px", "20px", "24px"]}
            h={["16px", "20px", "24px"]}
            borderRadius="50%"
          />
        )}
        {shadowcorn?.name && (
          <>
            <Box
              pl={["5px", "5px", "7px"]}
              textOverflow="ellipsis"
              whiteSpace="nowrap"
            >{`${shadowcorn.name} (${tokenId})`}</Box>
          </>
        )}
        {!shadowcorn?.name && (
          <Text pl={["5px", "5px", "7px"]} whiteSpace="nowrap">
            {tokenId}
          </Text>
        )}

        <Icon
          as={FiExternalLink}
          marginInlineStart="2px"
          my="auto"
          pb={["4px", "4px", "2px"]}
        />
      </Flex>
    </Link>
  );
};

export default ShadowcornRow;
