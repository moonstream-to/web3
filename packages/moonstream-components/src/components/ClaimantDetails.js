import React, { useContext } from "react";
import { Flex, Spinner, IconButton, Heading } from "@chakra-ui/react";
import Web3Context from "../core/providers/Web3Provider/context";
import { CloseIcon } from "@chakra-ui/icons";
import { BiTrash } from "react-icons/bi";
import { useDrop } from "../core/hooks/dropper";
import useSearch from "../core/hooks/useSearch";
const ClaimantDetails = ({ claimId, address, onClose }) => {
  const web3ctx = useContext(Web3Context);

  const { deleteClaimants } = useDrop({
    ctx: web3ctx,
    claimId: claimId,
  });

  const { search } = useSearch({
    pathname: `/admin/drops/${claimId}/claimants/search`,
    query: { address: address },
  });

  if (search.isLoading) return <Spinner size="sm" />;
  return (
    <Flex className="ClaimantDetails" direction={"row"} alignItems="baseline">
      {search.data?.address && (
        <>
          <Heading size="sm">Amount: {search.data.raw_amount}</Heading>
          <IconButton
            size="sm"
            colorScheme="orange"
            isLoading={deleteClaimants.isLoading}
            onClick={() => {
              deleteClaimants.mutate(
                { list: [address] },
                {
                  onSuccess: () => {
                    search.remove();
                    onClose();
                  },
                }
              );
            }}
            version="ghost"
            icon={<BiTrash />}
          ></IconButton>
        </>
      )}
      {!search.data?.address && <Heading size="sm">Not found</Heading>}
      <IconButton
        colorScheme="orange"
        onClick={onClose}
        size="sm"
        version="ghost"
        icon={<CloseIcon />}
      ></IconButton>
    </Flex>
  );
};
export default ClaimantDetails;
