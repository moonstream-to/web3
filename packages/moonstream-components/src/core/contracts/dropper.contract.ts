import { Dropper } from "../../../../../types/contracts/Dropper";
const dropperAbi = require("../../../../../abi/Dropper.json");
import Web3 from "web3";
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";

export const claimDrop =
  (dropperAddress: any, ctx: MoonstreamWeb3ProviderInterface) =>
  async ({
    message,
    blockDeadline,
    claimId,
    transactionConfig,
  }: {
    message: string;
    blockDeadline: string;
    claimId: string;
    transactionConfig?: any;
  }) => {
    console.log("claimDrop", message, blockDeadline, claimId, dropperAddress);
    const dropper = new ctx.web3.eth.Contract(dropperAbi) as any as Dropper;
    dropper.options.address = dropperAddress;
    const txConfig = { ...ctx.defaultTxConfig, ...transactionConfig };

    console.log("txConfig", txConfig);
    // console.log("message before", message);
    // console.log("message after", ctx.web3.utils.hexToBytes(message));

    const response = await dropper.methods
      .claim(claimId, blockDeadline, "0", `0x` + message)
      // .claim("1", "123", 123)
      .send(txConfig);
    return response;
  };

export const getState = (address: any, ctx: any) => async () => {
  const web3 = ctx.web3;
  const dropper = new web3.eth.Contract(dropperAbi) as any as Dropper;
  dropper.options.address = address;

  const ERC20_TYPE = await dropper.methods.ERC20_TYPE().call();
  const ERC721_TYPE = await dropper.methods.ERC721_TYPE().call();
  const ERC1155_TYPE = await dropper.methods.ERC1155_TYPE().call();
  const numClaims = await dropper.methods.numClaims().call();
  const owner = await dropper.methods.owner().call();
  const paused = await dropper.methods.paused().call();

  return { ERC20_TYPE, ERC721_TYPE, ERC1155_TYPE, numClaims, owner, paused };
};

export const getClaim = (address: any, ctx: any) => async (claimId: string) => {
  const web3 = ctx.web3;
  const dropper = new web3.eth.Contract(dropperAbi) as any as Dropper;
  dropper.options.address = address;

  const claim = await dropper.methods.getClaim(claimId).call();
  const status = await dropper.methods
    .getClaimStatus(claimId, ctx.account)
    .call();

  return { claim, status };
};
