import React from "react";
import { Flex, ScaleFade } from "@chakra-ui/react";
import Details from "moonstream-components/src/components/Dropper/Details";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
import { useRouter } from "moonstream-components/src/core/hooks";
import Drop from "moonstream-components/src/components/Dropper/Drop";

const Drops = () => {
  const router = useRouter();
  const { dropId } = router.query;

  if (!dropId) return "drop Id must be specifed";
  return (
    <ScaleFade in transition={"2s"}>
      <Flex>
        <Drop dropId={dropId}>
          <Details dropId={dropId} />
        </Drop>
      </Flex>
    </ScaleFade>
  );
};

Drops.getLayout = getLayout;
export default Drops;
