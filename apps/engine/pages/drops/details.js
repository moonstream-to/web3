import React, { useContext } from "react";
import { Flex, ScaleFade } from "@chakra-ui/react";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
import Details from "moonstream-components/src/components/Dropper/Details";

import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
import { useRouter } from "moonstream-components/src/core/hooks";
import { targetChain } from "moonstream-components/src/core/providers/Web3Provider";
import useDrop from "moonstream-components/src/core/hooks/useDrop";
import Drop from "moonstream-components/src/components/Dropper/Drop";

const Drops = () => {
  const router = useRouter();
  const { dropId } = router.query;
  const web3ctx = useContext(Web3Context);

  const { claim, claimants } = useDrop({
    targetChain,
    ctx: web3ctx,
    claimId: dropId,
  });

  if (!dropId) return "drop Id must be specifed";
  if (!claim) return "";
  return (
    <ScaleFade in transition={"2s"}>
      <Flex>
        <Drop claim={claim} title={claim.title}>
          <Details dropId={dropId} claimants={claimants} />
        </Drop>
      </Flex>
    </ScaleFade>
  );
};

Drops.getLayout = getLayout;
export default Drops;
