import { Dropper } from "../../../../../types/contracts/Dropper";
const dropperAbi = require("../../../../../abi/Dropper.json");
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";

export const claimDrop =
  (dropperAddress: any, ctx: MoonstreamWeb3ProviderInterface) =>
  async ({
    message,
    blockDeadline,
    claimId,
    transactionConfig,
    amount,
  }: {
    message: string;
    blockDeadline: string;
    claimId: string;
    transactionConfig?: any;
    amount: string;
  }) => {
    const dropper = new ctx.web3.eth.Contract(dropperAbi) as any as Dropper;
    dropper.options.address = dropperAddress;
    const txConfig = { ...ctx.defaultTxConfig, ...transactionConfig };

    const response = await dropper.methods
      .claim(claimId, blockDeadline, amount, `0x` + message)
      // .claim("1", "123", 123)
      .send(txConfig);
    return response;
  };

export const getState = (address: any, ctx: any) => async () => {
  const web3 = ctx.web3;
  const dropper = new web3.eth.Contract(dropperAbi) as any as Dropper;
  dropper.options.address = address;

  //eslint-disable-next-line
  const ERC20_TYPE = await dropper.methods.ERC20_TYPE().call();
  //eslint-disable-next-line
  const ERC721_TYPE = await dropper.methods.ERC721_TYPE().call();
  //eslint-disable-next-line
  const ERC1155_TYPE = await dropper.methods.ERC1155_TYPE().call();
  const numClaims = await dropper.methods.numClaims().call();
  const owner = await dropper.methods.owner().call();
  const paused = await dropper.methods.paused().call();

  return { ERC20_TYPE, ERC721_TYPE, ERC1155_TYPE, numClaims, owner, paused };
};

/*
  @dev get claim returns array of following solidity strucutre:

    uint256 public ERC20_TYPE = 20;
    uint256 public ERC721_TYPE = 721;
    uint256 public ERC1155_TYPE = 1155;
    uint256 public TERMINUS_MINTABLE_TYPE = 1;

    struct ClaimableToken {
        uint256 tokenType;
        address tokenAddress; // address of the token
        uint256 tokenId;
        uint256 amount;
    }
*/
export const getClaim = (address: any, ctx: any) => async (claimId: string) => {
  const web3 = ctx.web3;
  const dropper = new web3.eth.Contract(dropperAbi) as any as Dropper;
  dropper.options.address = address;

  const claim = await dropper.methods.getClaim(claimId).call();
  const status = await dropper.methods
    .getClaimStatus(claimId, ctx.account)
    .call();
  const claimUri = await dropper.methods.claimUri(claimId).call();
  const signer = await dropper.methods.getSignerForClaim(claimId).call();

  return { claim, status, claimUri, signer };
};

export const getSignerForClaim =
  (address: any, ctx: any) => async (claimId: string) => {
    const web3 = ctx.web3;
    const dropper = new web3.eth.Contract(dropperAbi) as any as Dropper;
    dropper.options.address = address;

    const result = await dropper.methods.getSignerForClaim(claimId).call();

    return result;
  };

export const createClaim =
  (dropperAddress: any, ctx: MoonstreamWeb3ProviderInterface) =>
  async ({
    rewardAddress,
    rewardType,
    rewardId,
    transactionConfig,
    amount,
  }: {
    rewardType: string;
    rewardAddress: string;
    rewardId: string;
    transactionConfig?: any;
    amount: string;
  }) => {
    const dropper = new ctx.web3.eth.Contract(dropperAbi) as any as Dropper;
    dropper.options.address = dropperAddress;
    const txConfig = { ...ctx.defaultTxConfig, ...transactionConfig };

    const response = await dropper.methods
      .createClaim(rewardType, rewardAddress, rewardId, amount)
      .send(txConfig);
    return response;
  };
