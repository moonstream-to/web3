import React, { useContext } from "react";
import { chakra, Flex, Spinner } from "@chakra-ui/react";
import { targetChain } from "../../core/providers/Web3Provider";
import Web3Context from "../../core/providers/Web3Provider/context";
import useDrops from "../../core/hooks/dropper/useDrops";
import useClaim from "../../core/hooks/dropper/useDrop";
import Claimers from "../Claimers";

const _Drop = ({
  dropId,
  ...props
}: {
  dropId: string;
  claimants: Array<String>;
}) => {
  const web3ctx = useContext(Web3Context);

  const { adminClaims } = useDrops({
    targetChain: targetChain,
    ctx: web3ctx,
  });

  const {
    claim,
    claimants,
    deleteClaimants,
    setClaimantsPage,
    claimantsPage,
    setClaimantsPageSize,
    claimantsPageSize,
  } = useClaim({
    targetChain,
    ctx: web3ctx,
    claimId: dropId,
  });

  if (!claim || !claimants.data || !adminClaims.data || adminClaims.isLoading)
    return <Spinner />;

  return (
    <Flex
      borderRadius={"md"}
      bgColor="blue.800"
      w="100%"
      direction={"column"}
      p={4}
      mt={2}
      textColor={"gray.300"}
      {...props}
    >
      <Flex bgColor={"blue.1200"} borderRadius="md" p={2} direction="column">
        <Claimers
          list={claimants.data}
          onDeleteClaimant={(address: string) => {
            deleteClaimants.mutate({ list: [address] });
          }}
          setPage={setClaimantsPage}
          setLimit={setClaimantsPageSize}
          page={claimantsPage}
          limit={claimantsPageSize}
          hasMore={claimants.data.length == claimantsPageSize ? true : false}
        />
      </Flex>
    </Flex>
  );
};

const Drop = chakra(_Drop);

export default Drop;
