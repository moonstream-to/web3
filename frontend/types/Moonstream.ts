import Web3 from "web3";

export interface WalletStatesInterface {
  ONBOARD: string;
  CONNECT: string;
  CONNECTED: string;
  WRONG_CHAIN: string;
}

export interface ReactWeb3ProviderInterface {
  web3: Web3;
  onConnectWalletClick: () => void;
  buttonText: string;
  WALLET_STATES: WalletStatesInterface;
  account: string;
  chainId: number | void;
  defaultTxConfig: any;
}
