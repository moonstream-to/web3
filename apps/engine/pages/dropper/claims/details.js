import React from "react";
import { Flex, ScaleFade } from "@chakra-ui/react";
import Details from "moonstream-components/src/components/Dropper/Details";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
import { useRouter } from "moonstream-components/src/core/hooks";
import Claim from "moonstream-components/src/components/Dropper/Claim";

const Drops = () => {
  const router = useRouter();
  const { claimId, contractAddress, claimIdx } = router.query;

  if (!claimId) return "drop Id must be specifed";
  if (!contractAddress) return "contract address plz";
  if (!claimIdx) return "claimIdx  plz";
  return (
    <ScaleFade in transition={"2s"}>
      <Flex>
        <Claim
          claimId={claimId}
          dropperAddress={contractAddress}
          claimIdx={claimIdx}
        >
          <Details dropId={claimId} />
        </Claim>
      </Flex>
    </ScaleFade>
  );
};

Drops.getLayout = getLayout;
export default Drops;
