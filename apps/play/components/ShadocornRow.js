import { HStack, Text, Image, Link, Box } from "@chakra-ui/react";
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
      <HStack>
        {shadowcorn && (
          <Image
            alt="sc"
            src={shadowcorn.image}
            w={["16px", "20px", "24px"]}
            h={["16px", "20px", "24px"]}
            borderRadius="4px"
          />
        )}
        {shadowcorn?.name && (
          <>
            <Box
              pl={["2px", "5px", "7px"]}
              textOverflow="ellipsis"
              whiteSpace="nowrap"
            >{`${shadowcorn.name} - ${tokenId}`}</Box>
          </>
        )}
        {!shadowcorn?.name && (
          <Text pl={["2px", "5px", "7px"]} whiteSpace="nowrap">
            {tokenId}
          </Text>
        )}

        {/* <Icon
          as={FiExternalLink}
          ml="0px" //{["2px", "5px", "7px"]}
          pb="5px"
          pl="0px"
        /> */}
      </HStack>
    </Link>
  );
};

export default ShadowcornRow;
