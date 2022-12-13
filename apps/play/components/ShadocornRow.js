import { HStack, Text, Icon, Image, Link } from "@chakra-ui/react";
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
      <HStack>
        {shadowcorn && (
          <Image
            alt="sc"
            src={shadowcorn.image}
            w="24px"
            h="24px"
            borderRadius="4px"
          />
        )}
        <Text pl="7px">{shadowcorn?.name ?? tokenId}</Text>)
        <Icon as={FiExternalLink} ml="10px" />
      </HStack>
    </Link>
  );
};

export default ShadowcornRow;
