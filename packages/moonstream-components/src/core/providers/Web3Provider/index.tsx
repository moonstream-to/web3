import React from "react";
import Web3Context, { WALLET_STATES } from "./context";
import Web3 from "web3";
import {
  ChainInterface,
  GetMethodsAbiType,
} from "../../../../../../types/Moonstream";

declare global {
  interface Window {
    ethereum: any;
    web3: Web3;
  }
}

interface TokenInterface {
  address: string;
  deadline: number;
  signed_message: string;
}

export const getMethodsABI: typeof GetMethodsAbiType = (abi, name) => {
  const index = abi.findIndex(
    (item) => item.name === name && item.type == "function"
  );
  if (index !== -1) {
    const item = abi[index];
    return item;
  } else throw "accesing wrong abi element";
};

export const chains: { [index: string]: ChainInterface } = {
  local: {
    chainId: 1337,
    name: "local",
    rpcs: ["http://127.0.0.1:8545"],
  },
  mumbai: {
    chainId: 80001,
    name: "mumbai",
    rpcs: [
      "https://rpc-mumbai.matic.today",
      "https://matic-mumbai.chainstacklabs.com",
      "https://rpc-mumbai.maticvigil.com",
      "https://matic-testnet-archive-rpc.bwarelabs.com",
    ],
  },
  polygon: {
    chainId: 137,
    name: "polygon",
    rpcs: [
      "https://polygon-rpc.com",
      "https://rpc-mainnet.matic.network",
      "https://matic-mainnet.chainstacklabs.com",
      "https://rpc-mainnet.maticvigil.com",
      "https://rpc-mainnet.matic.quiknode.pro",
      "https://matic-mainnet-full-rpc.bwarelabs.com",
    ],
  },
};

const signAccessToken = async (account: string) => {
  const msgParams = JSON.stringify({
    domain: {
      // Give a user friendly name to the specific contract you are signing for.
      name: "MoonstreamAuthorization",
      // Just let's you know the latest version. Definitely make sure the field name is correct.
      version: "1",
    },

    // Defining the message signing data content.
    message: {
      // "_name_": "MoonstreamAuthorization", // The value to sign
      address: account,
      // "_version_": "1",
      deadline: Math.floor(new Date().getTime() / 1000) + 24 * 60 * 60,
      // deadline: "1651008410"
    },
    // Refers to the keys of the *types* object below.
    primaryType: "MoonstreamAuthorization",
    types: {
      // TODO: Clarify if EIP712Domain refers to the domain the contract is hosted on
      EIP712Domain: [
        { name: "name", type: "string" },
        { name: "version", type: "string" },
      ],
      // Refer to PrimaryType
      MoonstreamAuthorization: [
        {
          type: "address",
          name: "address",
        },
        {
          type: "uint256",
          name: "deadline",
        },
      ],
    },
  });

  const result = await window.ethereum.request({
    method: "eth_signTypedData_v4",
    params: [account, msgParams],
    from: account,
  });

  localStorage.setItem(
    "APP_ACCESS_TOKEN",
    Buffer.from(
      JSON.stringify({
        address: account,
        deadline: JSON.parse(msgParams).message.deadline,
        signed_message: result,
      }),
      "utf-8"
    ).toString("base64")
  );
  // localStorage.setItem(
  //   "APP_ACCESS_TOKEN_DEADLINE",
  //   JSON.parse(msgParams).message.deadline
  // );
};

if (!process.env.NEXT_PUBLIC_ENGINE_TARGET_CHAIN)
  throw "NEXT_PUBLIC_ENGINE_TARGET_CHAIN not defined";
export const targetChain =
  chains[`${process.env.NEXT_PUBLIC_ENGINE_TARGET_CHAIN}`];

const Web3Provider = ({ children }: { children: JSX.Element }) => {
  const [web3] = React.useState<Web3>(new Web3(null));
  web3.eth.transactionBlockTimeout = 100;
  // TODO: this flag should allow to read revert messages
  // However there seems to be abug in web3js, and setting this flag will upset metamsk badly..
  // issue: https://github.com/ChainSafe/web3.js/issues/4787
  // web3.eth.handleRevert = true;
  const [buttonText, setButtonText] = React.useState(WALLET_STATES.ONBOARD);
  const [account, setAccount] = React.useState<string>("");
  const [chainId, setChainId] = React.useState<number>(0);

  const setWeb3ProviderAsWindowEthereum = async () => {
    let wasSetupSuccess = false;
    await window.ethereum
      .request({ method: "eth_requestAccounts" })
      .then(() => {
        web3.setProvider(window.ethereum);
        wasSetupSuccess = true;
      });
    return wasSetupSuccess;
  };

  const onConnectWalletClick = () => {
    if (window.ethereum) {
      setWeb3ProviderAsWindowEthereum().then((result) => {
        if (result) console.log("wallet setup was successfull");
        else
          console.warn(
            "wallet setup failed, should go in fallback mode immediately"
          );
        setButtonText(result ? WALLET_STATES.CONNECTED : WALLET_STATES.CONNECT);
      });
    }
  };

  React.useLayoutEffect(() => {
    if (web3.currentProvider) {
      web3?.eth.getChainId().then((id) => setChainId(id));
    }
  }, [web3.currentProvider, web3?.eth]);

  React.useLayoutEffect(() => {
    const changeChain = async () => {
      try {
        await window.ethereum
          .request({
            method: "wallet_switchEthereumChain",
            params: [{ chainId: `0x${targetChain.chainId.toString(16)}` }],
          })
          .then(() => web3?.eth.getChainId().then((id) => setChainId(id)));
      } catch (switchError: any) {
        // This error code indicates that the chain has not been added to MetaMask.
        if (switchError.code === 4902) {
          try {
            await window.ethereum.request({
              method: "wallet_addEthereumChain",
              params: [
                {
                  chainId: `${targetChain.chainId}`,
                  chainName: targetChain.name,
                  rpcUrls: targetChain.rpcs,
                },
              ],
            });
          } catch (addError) {
            // handle "add" error
          }
        }
        // handle other "switch" errors
      }
    };

    if (web3.currentProvider && chainId) {
      if (chainId) {
        if (chainId === targetChain.chainId) {
          //we are on matic
        } else {
          //we are not on matic
          changeChain();
        }
      }
    }
  }, [chainId, web3.currentProvider, web3?.eth]);

  React.useLayoutEffect(() => {
    if (chainId === targetChain.chainId && web3.currentProvider) {
      web3.eth.getAccounts().then((accounts) => setAccount(accounts[0]));
    }
  }, [chainId, web3.currentProvider, web3?.eth]);

  window?.ethereum?.on("chainChanged", () => window.location.reload());
  window?.ethereum?.on("accountsChanged", (_accounts: Array<string>) => {
    if (chainId === targetChain.chainId && web3.currentProvider) {
      setAccount(web3.utils.toChecksumAddress(_accounts[0]));
    }
  });

  React.useLayoutEffect(() => {
    if (web3.currentProvider && chainId) {
      if (chainId === targetChain.chainId) {
        setButtonText(WALLET_STATES.CONNECTED);
      } else {
        setButtonText(WALLET_STATES.WRONG_CHAIN);
      }
    } else {
      if (!window.ethereum) {
        setButtonText(WALLET_STATES.ONBOARD);
      } else {
        setButtonText(WALLET_STATES.CONNECT);
      }
    }
  }, [web3.currentProvider, chainId]);

  React.useEffect(() => {
    if (window?.ethereum?.selectedAddress) {
      setWeb3ProviderAsWindowEthereum().then((result) => {
        if (result) console.log("wallet setup was successfull");
        else
          console.warn(
            "wallet setup failed, should go in fallback mode immediately"
          );
        setButtonText(result ? WALLET_STATES.CONNECTED : WALLET_STATES.CONNECT);
      });
      //  ÷
    }
    //eslint-disable-next-line
  }, []);

  React.useEffect(() => {
    const outDated = (deadline: any) => {
      if (!deadline) return true;
      if (Number(deadline) <= Math.floor(new Date().getTime() / 1000))
        return true;
      return false;
    };

    const token = localStorage.getItem("APP_ACCESS_TOKEN") ?? "";
    const stringToken = Buffer.from(token, "base64").toString("ascii");
    const objectToken: TokenInterface =
      stringToken !== ""
        ? JSON.parse(`${stringToken}`)
        : { address: null, deadline: null, signed_message: null };

    if (web3?.utils.isAddress(account)) {
      if (
        objectToken?.address !== account ||
        outDated(objectToken?.deadline) ||
        !objectToken.signed_message
      ) {
        signAccessToken(account);
      }
    }
    //eslint-disable-next-line
  }, [account]);

  const defaultTxConfig = { from: account };

  return (
    <Web3Context.Provider
      value={{
        web3: web3,
        onConnectWalletClick,
        buttonText,
        WALLET_STATES,
        account,
        chainId,
        defaultTxConfig,
        signAccessToken,
        getMethodsABI,
      }}
    >
      {children}
    </Web3Context.Provider>
  );
};

export default Web3Provider;
