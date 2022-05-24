import React from "react";
const abi = require("../../../../abi/MockErc20.json");
import ContractInterface from "moonstream-components/src/components/ContractInteface";
import { useRouter } from "moonstream-components/src/core/hooks";
const NewDrop = () => {
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
export default NewDrop;
