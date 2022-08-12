import { useMutation, useQuery } from "react-query";
import { getTokenState, getSpenderState } from "../contracts/erc20.contracts";
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";
import { MockErc20 } from "../../../../../types/contracts/MockErc20";
import { AbiItem } from "web3-utils";
import useToast from "./useToast";
const erc20abi: AbiItem = require("../../../../../abi/MockErc20.json");

const useERC20 = ({
  contractAddress,
  spender,
  ctx,
}: {
  contractAddress?: string;
  spender: string;
  ctx: MoonstreamWeb3ProviderInterface;
}) => {
  const erc20contract = new ctx.web3.eth.Contract(erc20abi) as any as MockErc20;
  erc20contract.options.address = contractAddress ?? "";
  const toast = useToast();
  const tokenState = useQuery(
    [
      "ERC20",
      "TokenState",
      { contractAddress: contractAddress, chainId: ctx.targetChain?.chainId },
    ],
    () => getTokenState({ ctx })(contractAddress ?? ""),
    {
      onSuccess: () => {},
      enabled:
        !!contractAddress &&
        ctx.web3?.utils.isAddress(contractAddress) &&
        ctx.web3?.utils.isAddress(ctx.account) &&
        !!ctx.chainId &&
        ctx.chainId === ctx.targetChain?.chainId,
    }
  );

  const spenderState = useQuery(
    [
      "ERC20",
      "SpenderState",
      {
        contractAddress: contractAddress,
        chainId: ctx.targetChain?.chainId,
        account: ctx.account,
        spender: spender,
      },
    ],
    () =>
      getSpenderState({ ctx, spender, contractAddress: contractAddress ?? "" }),
    {
      onSuccess: () => {},
      enabled:
        !!contractAddress &&
        ctx.web3?.utils.isAddress(contractAddress) &&
        ctx.web3?.utils.isAddress(ctx.account) &&
        !!ctx.chainId &&
        ctx.chainId === ctx.targetChain?.chainId &&
        ctx.web3?.utils.isAddress(spender),
    }
  );

  const commonProps = {
    onSuccess: () => {
      toast("Successfully updated contract", "success");
      spenderState.refetch();
    },
    onError: () => {
      toast("Something went wrong", "error");
    },
  };
  const setSpenderAllowance = useMutation(
    (amount: string) =>
      erc20contract.methods
        .approve(spender, amount)
        .send({ from: ctx.account }),
    { ...commonProps }
  );

  return { tokenState, spenderState, setSpenderAllowance };
};

export default useERC20;
