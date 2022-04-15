import { createContext } from "react";
import Web3 from "web3";
import {
  WalletStatesInterface,
  ReactWeb3ProviderInterface,
} from "../../../../types/Moonstream";

export enum txStatus {
  READY = 0,
  SUCCESS,
  ERROR,
  LOADING,
}

export interface web3MethodCall {
  status: txStatus;
  send: (...args: Array<any>) => void;
  data: any;
}

export const WALLET_STATES: WalletStatesInterface = {
  ONBOARD: "Install MetaMask!",
  CONNECT: "Connect with Metamask",
  CONNECTED: "Connected",
  WRONG_CHAIN: "Please select polygon chain in metamask",
};

const Web3Context = createContext<ReactWeb3ProviderInterface>({
  web3: new Web3(null),
  onConnectWalletClick: () => console.error("not intied"),
  buttonText: "",
  WALLET_STATES: WALLET_STATES,
  account: "",
  chainId: undefined,
  defaultTxConfig: {},
});

export default Web3Context;
