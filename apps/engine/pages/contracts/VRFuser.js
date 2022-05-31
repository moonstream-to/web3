import React from "react";
const abi = require("../../../../abi/MockVRFUser.json");
import ContractInterface from "moonstream-components/src/components/ContractInteface";
import { useRouter } from "moonstream-components/src/core/hooks";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
const Contract = () => {
  const router = useRouter();

  const { contractAddress } = router.query;
  return (
    <ContractInterface
      abi={abi}
      initalContractAddress={contractAddress ?? ""}
      w="100%"
    />
  );
};
Contract.getLayout = getLayout;
export default Contract;
