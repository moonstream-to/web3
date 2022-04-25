import React from "react";
import Web3Context, { WALLET_STATES } from "./context";
import Web3 from "web3";
import { getweb3Auth, postweb3Auth } from "../../services/terminus.service";
import { getTime } from "../../services/moonstream-engine.service";

declare global {
  interface Window {
    ethereum: any;
    web3: Web3;
  }
}

export const chains: { [index: string]: any } = {
  local: {
    chainId: 1337,
    name: "local",
    rpcs: ["http://127.0.0.1:8545"],
  },
  matic_mumbai: {
    chainId: 80001,
    name: "Matic mumbai",
    rpcs: [
      "https://rpc-mumbai.matic.today",
      "https://matic-mumbai.chainstacklabs.com",
      "https://rpc-mumbai.maticvigil.com",
      "https://matic-testnet-archive-rpc.bwarelabs.com",
    ],
  },
  matic: {
    chainId: 137,
    name: "Matic mainnet",
    rpcs: [
      "https://rpc-mainnet.matic.network",
      "https://matic-mainnet.chainstacklabs.com",
      "https://rpc-mainnet.maticvigil.com",
      "https://rpc-mainnet.matic.quiknode.pro",
      "https://matic-mainnet-full-rpc.bwarelabs.com",
    ],
  },
};

if (!process.env.NEXT_PUBLIC_TARGET_CHAIN)
  throw "NEXT_PUBLIC_TARGET_CHAIN not defined";
export const targetChain = chains[`${process.env.NEXT_PUBLIC_TARGET_CHAIN}`];

const Web3Provider = ({ children }: { children: JSX.Element }) => {
  const [web3] = React.useState<Web3>(new Web3(null));
  const [buttonText, setButtonText] = React.useState(WALLET_STATES.ONBOARD);
  const [account, setAccount] = React.useState<string>("");
  const [chainId, setChainId] = React.useState<number | void>();

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
      console.log("wallet provider detected -> connecting wallet");
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
      console.log("web3 is getting chain id");
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
      console.log(
        "Checking that",
        chainId,
        "corresponds to selected target chain id:",
        targetChain.chainId
      );
      if (chainId) {
        if (chainId === targetChain.chainId) {
          //we are on matic
          console.log("chain id is correct");
        } else {
          //we are not on matic
          console.log("requesting to change chain Id", chainId);
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

  // React.useEffect(() => {
  //   if (
  //     !localStorage.getItem("APP_ACCESS_TOKEN") &&
  //     web3?.utils.isAddress(account)
  //   ) {
  //     console.log("x0x entring");
  //     getweb3Auth(account, chainId).then(async (resp: any) => {
  //       // console.log("resp", resp?.data.quest);

  //       const quest = resp?.data.quest;
  //       console.log("x0x got quest", quest);

  //       const signature = await window.ethereum.request({
  //         method: "personal_sign",
  //         params: [quest, account],
  //       });
  //       // const signature = await web3Provider.web3.eth.personal.sign(
  //       //   data.data.quest,
  //       //   web3Provider.account
  //       // );
  //       const response = await postweb3Auth(
  //         account,
  //         targetChain.chainId
  //       )(signature);
  //       console.log("token:", response.data);
  //       const token = response.data;
  //       if (token) {
  //         console.log("x0x got token");
  //         localStorage.setItem("APP_ACCESS_TOKEN", token);
  //       }
  //     });
  //   }
  // }, [account, chainId, web3.utils]);

  React.useEffect(() => {
    if (
      !localStorage.getItem("APP_ACCESS_TOKEN") &&
      web3?.utils.isAddress(account)
    ) {
      console.log("auth flow entring");

      // const message = "blablabla";

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

      // if(!window?.ethereum?.currentProvider) throw("ERRRRROR");
      // console.dir(window.ethereum)
      console.log("chain id", chainId)
      window.ethereum.sendAsync(
        {
          method: "eth_signTypedData_v4",
          params: [account, msgParams],
          from: account,
        },
        (err: Error, signedMessage: any) => {
          console.log(
            "signedMessage",
            signedMessage,
            account,
            JSON.parse(msgParams).message.deadline
          );
        }
      );
    }
  }, [account, chainId, web3.utils, window.ethereum.currentProvider]);

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
      }}
    >
      {children}
    </Web3Context.Provider>
  );
};

export default Web3Provider;
