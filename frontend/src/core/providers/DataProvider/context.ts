import React, { createContext } from "react";
import { BaseContract } from "../../../../types/contracts/types";

export interface ContractsHolder {
  [key: string]: BaseContract;
}

export interface DataContextType {
  dispatchContracts: React.Dispatch<any>;
  contracts: ContractsHolder;
}
const DataContext = createContext<DataContextType>({
  dispatchContracts: () => null,
  contracts: {},
});

export default DataContext;
