import React from "react";
import { Flex, ScaleFade } from "@chakra-ui/react";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
import { useRouter } from "moonstream-components/src/core/hooks";
import TerminusPool from "moonstream-components/src/components/TerminusPool";

const Drops = () => {
  const router = useRouter();
  const { poolId, contractAddress } = router.query;

  if (!poolId) return "pool Id must be specifed";
  return (
    <ScaleFade in transition={"2s"}>
      <Flex w="100%" justifyContent={"center"}>
        <TerminusPool
          // maxW="600px"
          poolId={poolId}
          address={contractAddress}
          justifySelf="center"
        ></TerminusPool>
      </Flex>
    </ScaleFade>
  );
};

Drops.getLayout = getLayout;
export default Drops;
