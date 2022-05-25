import React, { useContext } from "react";

import {
  Flex,
  Spinner,
  UnorderedList,
  ListItem,
  IconButton,
  Heading,
} from "@chakra-ui/react";
import Web3Context from "../core/providers/Web3Provider/context";
import { targetChain } from "../core/providers/Web3Provider";
import CopyButton from "./CopyButton";
import { CloseIcon } from "@chakra-ui/icons";
import { BiTrash } from "react-icons/bi";
import { useClaim } from "../core/hooks/dropper";
const ClaimantDetails = ({ claimId, address, onClose, onDeleteClaimant }) => {
  const web3ctx = useContext(Web3Context);

  const { signature } = useClaim({
    targetChain,
    ctx: web3ctx,
    claimId: claimId,
    claimantAddress: address,
  });
  if (signature.isLoading) return <Spinner />;
  return (
    <Flex className="ClaimantDetails" direction={"row"}>
      {signature.data?.signature && (
        <>
          <CopyButton text={signature.data.signature}>Signature</CopyButton>
          <UnorderedList>
            <ListItem>Deadline: {signature.data.block_deadline}</ListItem>
            <ListItem>Amount: {signature.data.claim_id}</ListItem>
          </UnorderedList>
          <IconButton
            colorScheme="orange"
            onClick={() => onDeleteClaimant(address)}
            version="ghost"
            icon={<BiTrash />}
          ></IconButton>
        </>
      )}
      {!signature.data?.signature && <Heading>Not found</Heading>}
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
