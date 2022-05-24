import React from "react";
const dropperAbi = require("../../../../abi/Dropper.json");
import ContractInterface from "moonstream-components/src/components/ContractInteface";
import { useRouter } from "moonstream-components/src/core/hooks";
const NewDrop = () => {
  const router = useRouter();

  const { contractAddress } = router.query;
  return (
    <ContractInterface
      abi={dropperAbi}
      initalContractAddress={contractAddress ?? ""}
      w="100%"
    />
  );
};
export default NewDrop;
