import React from "react";
import { Flex, IconButton } from "@chakra-ui/react";
import { ArrowLeftIcon, ArrowRightIcon } from "@chakra-ui/icons";

const ClaimPageControls = ({ pageOptions, refetch }) => {
  return (
    <Flex justifyContent="center">
      <IconButton
        icon={<ArrowLeftIcon />}
        onClick={() => {
          pageOptions.setOffset(
            Math.max(pageOptions.offset - pageOptions.limit, 0)
          );
          refetch();
        }}
        alignSelf="center"
      ></IconButton>
      <IconButton
        icon={<ArrowRightIcon />}
        onClick={() => {
          pageOptions.setOffset(
            parseInt(pageOptions.offset) + parseInt(pageOptions.limit)
          );
        }}
        alignSelf="center"
      ></IconButton>
    </Flex>
  );
};

export default ClaimPageControls;
