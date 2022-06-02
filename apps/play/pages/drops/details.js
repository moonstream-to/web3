import React, { useContext } from "react";

import { Flex, Spinner } from "@chakra-ui/react";
import Paginator from "moonstream-components/src/components/Paginator";
import ClaimCard from "moonstream-components/src/components/ClaimCard";
import usePlayerClaims from "moonstream-components/src/core/hooks/dropper/useClaims";
import { targetChain } from "moonstream-components/src/core/providers/Web3Provider";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
import { useRouter } from "moonstream-components/src/core/hooks";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
const DropDetails = () => {
  const router = useRouter();
  const web3Provider = useContext(Web3Context);
  const { dropperAddress } = router.query;
  const { playerClaims, page, pageSize, setPage, setPageSize } =
    usePlayerClaims({
      targetChain: targetChain,
      ctx: web3Provider,
      contractAddress: dropperAddress,
    });

  if (!dropperAddress) return "dropId must be specified";
  if (!web3Provider.account) return "connect with metamask";
  if (playerClaims.isLoading) return <Spinner />;
  return (
    <Flex className="DropDetails">
      <Paginator
        page={page}
        pageSize={pageSize}
        setLimit={setPageSize}
        setPage={setPage}
        paginatorKey={`dropList`}
        hasMore={playerClaims.data?.length == pageSize ? true : false}
        mx={20}
      >
        {playerClaims.data?.map((claim) => {
          return (
            <ClaimCard
              // mx={20}
              mt={2}
              key={`pc-${claim.dropper_claim_id}`}
              address={dropperAddress}
              drop={claim}
            />
          );
        })}
      </Paginator>
    </Flex>
  );
};

DropDetails.getLayout = getLayout;
export default DropDetails;
