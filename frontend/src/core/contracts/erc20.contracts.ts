import { MockErc20 } from "../../../types/contracts/MockErc20";
const erc20abi: AbiItem = require("../../../abi/MockErc20.json");
import Web3 from "web3";
import { ReactWeb3ProviderInterface } from "../../../types/Moonstream";
import BN from "bn.js";
import { AbiItem } from "web3-utils";

export const getTokenState =
  ({
    ctx,
    account,
    spender,
  }: {
    ctx: ReactWeb3ProviderInterface;
    account?: string;
    spender?: string;
  }) =>
  async (address: string) => {
    const erc20contract = new ctx.web3.eth.Contract(
      erc20abi
    ) as any as MockErc20;
    erc20contract.options.address = address;
    const balance = account
      ? await erc20contract.methods.balanceOf(account).call()
      : null;
    const spenderBalance = spender
      ? await erc20contract.methods.balanceOf(spender).call()
      : null;
    const allowance =
      spender && account
        ? await erc20contract.methods.allowance(account, spender).call()
        : null;
    const totalSupply = await erc20contract.methods.totalSupply().call();
    const symbol = await erc20contract.methods.symbol().call();
    const decimals = await erc20contract.methods.decimals().call();
    const name = await erc20contract.methods.name().call();
    return {
      totalSupply,
      symbol,
      decimals,
      name,
      balance,
      allowance,
      spenderBalance,
    };
  };
