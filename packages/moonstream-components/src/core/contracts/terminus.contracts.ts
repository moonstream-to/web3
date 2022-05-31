import { MockTerminus as TerminusFacet } from "../../../../../types/contracts/MockTerminus";

import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";

const terminusAbi = require("../../../../../abi/MockTerminus.json");
export const getTerminusFacetState =
  (ctx: MoonstreamWeb3ProviderInterface, terminusAddress: string) =>
  async () => {
    const terminusFacet = new ctx.web3.eth.Contract(
      terminusAbi
    ) as any as TerminusFacet;
    terminusFacet.options.address = terminusAddress;

    const poolBasePrice = await terminusFacet.methods.poolBasePrice().call();
    const paymentToken = await terminusFacet.methods.paymentToken().call();
    const contractURI = await terminusFacet.methods.contractURI().call();
    const totalPools = await terminusFacet.methods.totalPools().call();
    const controller = await terminusFacet.methods.terminusController().call();
    return {
      poolBasePrice,
      paymentToken,
      contractURI,
      totalPools,
      controller,
    };
  };

export const getTerminusFacetPoolState =
  (ctx: MoonstreamWeb3ProviderInterface, address: string, poolId: string) =>
  async () => {
    const terminusFacet = new ctx.web3.eth.Contract(
      terminusAbi
    ) as any as TerminusFacet;
    terminusFacet.options.address = address;

    const controller = await terminusFacet.methods
      .terminusPoolController(poolId)
      .call();
    const supply = await terminusFacet.methods
      .terminusPoolSupply(poolId)
      .call();
    const uri = await terminusFacet.methods.uri(poolId).call();
    const capacity = await terminusFacet.methods
      .terminusPoolCapacity(poolId)
      .call();

    let accountBalance: any = "0";

    if (ctx.account) {
      accountBalance = await terminusFacet.methods
        .balanceOf(ctx.account, poolId)
        .call();
    }

    return { controller, supply, uri, capacity, accountBalance };
  };

export const balanceOfAddress =
  (
    userAddress: string,
    terminusAddress: string,
    terminusPoolId: number,
    ctx: MoonstreamWeb3ProviderInterface
  ) =>
  () => {
    const terminusFacet = new ctx.web3.eth.Contract(
      terminusAbi
    ) as any as TerminusFacet;
    terminusFacet.options.address = terminusAddress;
    return terminusFacet.methods.balanceOf(userAddress, terminusPoolId).call();
  };
