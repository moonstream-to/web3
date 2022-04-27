import Web3 from "web3/types";

export interface WalletStatesInterface {
  ONBOARD: String;
  CONNECT: String;
  CONNECTED: String;
  WRONG_CHAIN: String;
}
export interface ChainInterface {
  chainId: number;
  name: string;
  rpcs: Array<string>;
}

export interface MoonstreamWeb3ProviderInterface {
  web3: Web3;
  onConnectWalletClick: Function;
  buttonText: String;
  WALLET_STATES: WalletStatesInterface;
  account: string;
  chainId: number;
  defaultTxConfig: Object;
  signAccessToken: Function;
}