import React, { useContext } from "react";

import {
  Flex,
  Spinner,
  UnorderedList,
  ListItem,
  IconButton,
  Heading,
} from "@chakra-ui/react";
import useClaimant from "../core/hooks/dropper/useClaimant";
import Web3Context from "../core/providers/Web3Provider/context";
import { targetChain } from "../core/providers/Web3Provider";
import CopyButton from "./CopyButton";
import { CloseIcon } from "@chakra-ui/icons";
import { BiTrash } from "react-icons/bi";
const ClaimantDetails = ({ dropId, address, onClose, onDeleteClaimant }) => {
  const web3ctx = useContext(Web3Context);

  const { claim } = useClaimant({
    targetChain,
    ctx: web3ctx,
    dropId: dropId,
    claimantAddress: address,
  });
  if (claim.isLoading) return <Spinner />;
  return (
    <Flex className="ClaimantDetails" direction={"row"}>
      {claim.data?.signature && (
        <>
          <CopyButton text={claim.data.signature}>Signature</CopyButton>
          <UnorderedList>
            <ListItem>Deadline: {claim.data.block_deadline}</ListItem>
            <ListItem>Amount: {claim.data.claim_id}</ListItem>
          </UnorderedList>
          <IconButton
            colorScheme="orange"
            onClick={() => onDeleteClaimant(address)}
            version="ghost"
            icon={<BiTrash />}
          ></IconButton>
        </>
      )}
      {!claim.data?.signature && <Heading>Not found</Heading>}
      <IconButton
        colorScheme="orange"
        onClick={onClose}
        version="ghost"
        icon={<CloseIcon />}
      ></IconButton>
    </Flex>
  );
};
export default ClaimantDetails;
