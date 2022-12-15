import React from "react";
import Web3Context, { WALLET_STATES } from "./context";
import Web3 from "web3";
import { isOutdated, signAccessToken } from "@moonstream/web3auth";
import {
  ChainInterface,
  GetMethodsAbiType,
  supportedChains,
  TokenInterface,
} from "../../../../../../types/Moonstream";
import router from "next/router";
const REQUEST_SIGNATURE = process.env.NEXT_PUBLIC_REQUEST_SIGNATURE;

if (typeof REQUEST_SIGNATURE == "undefined") {
  console.error("REQUEST_SIGNATURE env var is not set!");
}

export const MAX_INT =
  "115792089237316195423570985008687907853269984665640564039457584007913129639935";

declare global {
  interface Window {
    ethereum: any;
    web3: Web3;
  }
}

const _askWalletProviderToChangeChain = async (
  targetChain: any,
  setChainId: any,
  web3: any
) => {
  if (targetChain?.chainId) {
    try {
      await window.ethereum
        .request({
          method: "wallet_switchEthereumChain",
          params: [{ chainId: `0x${targetChain?.chainId.toString(16)}` }],
        })
        .then(() => web3?.eth.getChainId().then((id: any) => setChainId(id)));
    } catch (switchError: any) {
      // This error code indicates that the chain has not been added to MetaMask.
      if (switchError.code === 4902) {
        try {
          await window.ethereum.request({
            method: "wallet_addEthereumChain",
            params: [
              {
                chainId: `${targetChain?.chainId}`,
                chainName: targetChain?.name,
                rpcUrls: targetChain?.rpcs,
              },
            ],
          });
        } catch (addError) {
          // handle "add" error
        }
      } else {
        throw switchError;
      }
      // handle other "switch" errors
    }
  } else {
    console.error("cannot change chain when targetChain is undefined");
  }
};
export const getMethodsABI: typeof GetMethodsAbiType = (abi, name) => {
  const index = abi.findIndex(
    (item) => item.name === name && item.type == "function"
  );
  if (index !== -1) {
    const item = abi[index];
    return item;
  } else throw "accesing wrong abi element";
};

export const chains: { [key in supportedChains]: ChainInterface } = {
  ethereum: {
    chainId: 1,
    name: "ethereum",
    rpcs: ["https://mainnet.infura.io/v3/"],
  },
  localhost: {
    chainId: 1337,
    name: "localhost",
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

export const chainByChainId: { [key: number]: string } = {
  1: "ethereum",
  1337: "localhost",
  80001: "mumbai",
  137: "polygon",
};

const isKnownChain = (_chainId: number) => {
  return Object.keys(chains).some((key) => {
    return chains[key as any as supportedChains].chainId == _chainId;
  });
};

const Web3Provider = ({ children }: { children: JSX.Element }) => {
  const [web3] = React.useState<Web3>(new Web3(null));
  const [polygonClient] = React.useState<Web3>(
    new Web3(new Web3.providers.HttpProvider("https://polygon-rpc.com"))
  );

  const _signAccessToken = async (account: string) => {
    if (web3.currentProvider) {
      const deadline = Math.floor(new Date().getTime() / 1000) + 24 * 60 * 60;
      const token = await signAccessToken(account, window.ethereum, deadline);

      localStorage.setItem("APP_ACCESS_TOKEN", token);
    }
  };

  const [targetChain, _setChain] = React.useState<ChainInterface | undefined>();

  web3.eth.transactionBlockTimeout = 100;
  // TODO: this flag should allow to read revert messages
  // However there seems to be abug in web3js, and setting this flag will upset metamsk badly..
  // issue: https://github.com/ChainSafe/web3.js/issues/4787
  // web3.eth.handleRevert = true;

  const [buttonText, setButtonText] = React.useState(WALLET_STATES.ONBOARD);
  const [account, setAccount] = React.useState<string>("");
  const [chainId, setChainId] = React.useState<number>(0);

  const changeChainFromWalletProvider = (_chainId: number) => {
    const chainKey = Object.keys(chains).find((_key) => {
      const key: supportedChains = _key as any as supportedChains;
      return chains[key].chainId == _chainId;
    }) as any as supportedChains | undefined;
    if (chainKey) {
      _setChain(chains[chainKey]);
      setButtonText(WALLET_STATES.CONNECTED);
    } else {
      _setChain(undefined);
      setButtonText(WALLET_STATES.UNKNOWN_CHAIN);
    }
  };

  const changeChainFromUI = (chainName: supportedChains) => {
    if (window?.ethereum) {
      _askWalletProviderToChangeChain(chains[chainName], setChainId, web3).then(
        () => {
          if (chainId) {
            _setChain(chains[chainName]);
            setButtonText(WALLET_STATES.CONNECTED);
          }
        },
        (err: any) => {
          console.error("changeChainFromUI:", err.message);
        }
      );
    }
  };

  const setWeb3ProviderAsWindowEthereum = async () => {
    let wasSetupSuccess = false;
    await window.ethereum
      .request({ method: "eth_requestAccounts" })
      .then(async () => {
        web3.setProvider(window.ethereum);
        web3.eth.getAccounts().then((accounts) => {
          setAccount(accounts[0]);
        });
        const _chainId = await web3.eth.getChainId();
        changeChainFromWalletProvider(_chainId);
        wasSetupSuccess = true;
      })
      .catch((err: any) => {
        if (err.code === 4001) {
          // EIP-1193 userRejectedRequest error
          // If this happens, the user rejected the connection request.
          console.log("Please connect to wallet.");
        } else {
          console.error(err);
        }
      });

    return wasSetupSuccess;
  };
  const onConnectWalletClick = async () => {
    if (window.ethereum) {
      await setWeb3ProviderAsWindowEthereum().then((result) => {
        if (result) console.log("wallet setup was successfull");
        else
          console.warn(
            "wallet setup failed, should go in fallback mode immediately"
          );
        setButtonText(result ? WALLET_STATES.CONNECTED : WALLET_STATES.CONNECT);
      });
    } else {
      router.push("https://metamask.io/download/");
    }
  };

  // When web3 has changed chainId -> represent it in state of provider
  React.useLayoutEffect(() => {
    if (web3.currentProvider) {
      web3?.eth.getChainId().then((id) => setChainId(id));
    }
  }, [web3.currentProvider, web3?.eth]);

  //when chainId, or web3 provider, or targetChain changed -> update current account in this state
  React.useLayoutEffect(() => {
    if (
      targetChain?.chainId &&
      chainId === targetChain?.chainId &&
      web3.currentProvider
    ) {
      web3.eth.getAccounts().then((accounts) => setAccount(accounts[0]));
    }
    // eslint-disable-next-line
    //
  }, [chainId, targetChain?.chainId, web3.currentProvider, web3.eth]);

  const handleMetamaskChainChanged = (_chainId: string) => {
    if (chainId) {
      setChainId(Number(_chainId));
    }
    changeChainFromWalletProvider(Number(_chainId));
  };
  const handleProviderAccountChanged = (_accounts: Array<string>) => {
    if (chainId === targetChain?.chainId && web3.currentProvider) {
      setAccount(web3.utils.toChecksumAddress(_accounts[0]));
    }
  };
  // On mount
  // -> start listen to chainId changed -> update current account state in this state
  // -> listen to connected -> setup state variables
  React.useEffect(() => {
    if (chainId && targetChain?.chainId) {
      window?.ethereum?.on("chainChanged", handleMetamaskChainChanged);
      window?.ethereum?.on("connect", setWeb3ProviderAsWindowEthereum);
      window?.ethereum?.on("accountsChanged", handleProviderAccountChanged);
    }

    return () => {
      window?.ethereum?.removeListener(
        "connect",
        setWeb3ProviderAsWindowEthereum
      );
      window?.ethereum?.removeListener(
        "chainChanged",
        handleMetamaskChainChanged
      );
      window?.ethereum?.removeListener(
        "accountsChanged",
        handleProviderAccountChanged
      );
    };
    //eslint-disable-next-line
  }, [chainId, targetChain?.chainId]);

  // When chainId or web3 or targetChain changes -> update button state
  React.useLayoutEffect(() => {
    if (web3.currentProvider && chainId && targetChain?.chainId && account) {
      if (isKnownChain(chainId)) {
        setButtonText(WALLET_STATES.CONNECTED);
      } else {
        setButtonText(WALLET_STATES.UNKNOWN_CHAIN);
      }
    } else {
      if (!window.ethereum) {
        setButtonText(WALLET_STATES.ONBOARD);
      } else {
        setButtonText(WALLET_STATES.CONNECT);
      }
    }
  }, [web3.currentProvider, chainId, targetChain, account]);

  // onMount check if there is provided address by provider already, if yes - set it in this state and provide to web3
  // As well as try to look up for chainId in list of supported chains
  React.useEffect(() => {
    if (window?.ethereum?.selectedAddress) {
      setWeb3ProviderAsWindowEthereum().then((result) => {
        if (result) {
          window?.ethereum
            ?.request({ method: "eth_chainId" })
            .then((_chainId: any) => {
              changeChainFromWalletProvider(parseInt(_chainId, 16));
            });
        } else
          console.warn(
            "provider setup failed, should go in fallback mode immediately"
          );

        setButtonText(result ? WALLET_STATES.CONNECTED : WALLET_STATES.CONNECT);
      });
      //  ÷
    }
    //eslint-disable-next-line
  }, []);

  React.useEffect(() => {
    if (REQUEST_SIGNATURE == "false") return;
    const token = localStorage.getItem("APP_ACCESS_TOKEN") ?? "";
    const stringToken = Buffer.from(token, "base64").toString("ascii");
    const objectToken: TokenInterface =
      stringToken !== ""
        ? JSON.parse(`${stringToken}`)
        : { address: null, deadline: null, signed_message: null };

    if (web3?.utils.isAddress(account)) {
      if (
        objectToken?.address !== account ||
        isOutdated(objectToken?.deadline) ||
        !objectToken.signed_message
      ) {
        _signAccessToken(account);
      }
    }
    //eslint-disable-next-line
  }, [account]);

  const defaultTxConfig = { from: account };
  return (
    <Web3Context.Provider
      value={{
        web3: web3,
        polygonClient: polygonClient,
        onConnectWalletClick,
        buttonText,
        WALLET_STATES,
        account,
        chainId,
        defaultTxConfig,
        signAccessToken: _signAccessToken,
        getMethodsABI,
        changeChain: changeChainFromUI,
        targetChain,
      }}
    >
      {children}
    </Web3Context.Provider>
  );
};

export default Web3Provider;
