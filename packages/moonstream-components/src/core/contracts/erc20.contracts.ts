import { MockErc20 } from "../../../../../types/contracts/MockErc20";
const erc20abi: AbiItem = require("../../../../../abi/MockErc20.json");
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";
import { AbiItem } from "web3-utils";

export const getTokenState =
  ({ ctx }: { ctx: MoonstreamWeb3ProviderInterface }) =>
  async (address: string) => {
    const erc20contract = new ctx.web3.eth.Contract(
      erc20abi
    ) as any as MockErc20;
    erc20contract.options.address = address;
    const totalSupply = await erc20contract.methods.totalSupply().call();
    const symbol = await erc20contract.methods.symbol().call();
    const decimals = await erc20contract.methods.decimals().call();
    const name = await erc20contract.methods.name().call();

    return {
      totalSupply,
      symbol,
      decimals,
      name,
    };
  };

export const getSpenderState = async ({
  spender,
  ctx,
  contractAddress,
  account,
}: {
  spender: string;
  ctx: MoonstreamWeb3ProviderInterface;
  contractAddress: string;
  account: string;
}) => {
  const erc20contract = new ctx.web3.eth.Contract(erc20abi) as any as MockErc20;
  erc20contract.options.address = contractAddress;
  const allowance =
    spender && spender
      ? await erc20contract.methods.allowance(account, spender).call()
      : null;
  const balance =
    spender && spender
      ? await erc20contract.methods.balanceOf(account).call()
      : null;

  return { allowance, balance };
};
