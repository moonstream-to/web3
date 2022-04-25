import Web3 from "web3/types";

export interface WalletStatesInterface {
  ONBOARD: String;
  CONNECT: String;
  CONNECTED: String;
  WRONG_CHAIN: String;
}

export interface MoonstreamWeb3ProviderInterface {
  web3: Web3;
  onConnectWalletClick: Function;
  buttonText: String;
  WALLET_STATES: WalletStatesInterface;
  account: string;
  chainId: string;
  defaultTxConfig: Object;
}
