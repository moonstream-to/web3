import { useMutation, useQuery } from "react-query";
import {
  getTerminusFacetPoolState,
  getTerminusFacetState,
  balanceOfAddress
} from "../contracts/terminus.contracts";
import { getTokenState } from "../contracts/erc20.contracts";
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";
import { MockTerminus } from "../../../../../types/contracts/MockTerminus";
import useToast from "./useToast";
import useURI from "./useLink";
const terminusAbi = require("../../../../../abi/MockTerminus.json");
import { hookCommon } from ".";
export interface TerminusHookArguments {
  poolId?: string;
  address: string;
  ctx: MoonstreamWeb3ProviderInterface;
}
export const useTerminusContract = ({
  poolId,
  address,
  ctx,
}: TerminusHookArguments) => {
  const terminusFacet = new ctx.web3.eth.Contract(
    terminusAbi
  ) as any as MockTerminus;
  terminusFacet.options.address = address;

  const toast = useToast();
  const contractState = useQuery(
    [
      ["terminusContract", "state"],
      { address: address, chainId: ctx.targetChain?.chainId },
    ],
    getTerminusFacetState(ctx, address),
    {
      ...hookCommon,
      onSuccess: () => {},
      enabled:
        ctx?.web3?.utils.isAddress(ctx.account) &&
        ctx.web3.utils.isAddress(address) &&
        !!ctx.chainId &&
        ctx.chainId === ctx.targetChain?.chainId,
    }
  );

  const paymentToken = useQuery(
    [
      ["terminusContract", "paymentToken"],
      {
        chainId: ctx.targetChain?.chainId,
        address: contractState.data?.paymentToken,
        terminusAddress: address,
      },
    ],
    (query: any) =>
      getTokenState({
        ctx,
      })(query.queryKey[1]?.address ?? ""),
    {
      ...hookCommon,
      onSuccess: () => {},
      enabled:
        !!contractState.data?.paymentToken &&
        ctx?.web3?.utils.isAddress(ctx.account) &&
        !!ctx.chainId &&
        ctx.chainId === ctx.targetChain?.chainId,
    }
  );

  const commonProps = {
    onSuccess: () => {
      toast("Successfully updated contract", "success");
      contractState.refetch();
    },
    onError: () => {
      toast("Something went wrong", "error");
    },
  };

  const setURI = useMutation(
    ({ uri }: { uri: string }) =>
      terminusFacet.methods.setContractURI(uri).send({ from: ctx.account }),
    { ...commonProps }
  );

  const setPoolBasePrice = useMutation(
    (value: string) =>
      terminusFacet.methods.setPoolBasePrice(value).send({ from: ctx.account }),
    { ...commonProps }
  );

  const setPaymentToken = useMutation(
    (value: string) =>
      terminusFacet.methods.setPaymentToken(value).send({ from: ctx.account }),
    { ...commonProps }
  );
  const setController = useMutation(
    (value: string) =>
      terminusFacet.methods.setController(value).send({ from: ctx.account }),
    { ...commonProps }
  );

  const newPool = useMutation(
    ({
      capacity,
      isBurnable,
      isTransferable,
    }: {
      capacity: string;
      isBurnable: boolean;
      isTransferable: boolean;
    }) =>
      terminusFacet.methods
        .createPoolV1(capacity, isTransferable, isBurnable)
        .send({ from: ctx.account }),
    { ...commonProps }
  );

  const poolState = useQuery(
    [
      ["terminusContract", "poolState"],
      { address: address, chainId: ctx.targetChain?.chainId, poolId: poolId },
    ],
    getTerminusFacetPoolState(ctx, address, poolId ?? ""),
    {
      ...hookCommon,
      onSuccess: () => {},
      enabled:
        !!poolId &&
        ctx?.web3?.utils.isAddress(ctx.account) &&
        ctx.web3.utils.isAddress(address) &&
        !!ctx.chainId &&
        ctx.chainId === ctx.targetChain?.chainId,
    }
  );

  const balanceOf = useQuery(
    [
      ["terminusContract", "balanceOf"],
      {
        address: address,
        chainId: ctx.targetChain?.chainId,
        poolId: poolId,
        currentUserAddress: ctx.account,
      },
    ],
    balanceOfAddress(ctx.account, address, Number(poolId), ctx),
    {
      ...hookCommon,
    }
  );

  const setPoolURI = useMutation(
    ({ uri, poolId }: { uri: string; poolId: string }) =>
      terminusFacet.methods.setURI(poolId, uri).send({ from: ctx.account }),
    { ...commonProps }
  );

  const setPoolController = useMutation(
    ({ newController, poolId }: { newController: string; poolId: string }) =>
      terminusFacet.methods
        .setPoolController(poolId, newController)
        .send({ from: ctx.account }),
    { ...commonProps }
  );

  const mint = useMutation(
    ({ to, poolId, amount }: { to: string; poolId: string; amount: string }) =>
      terminusFacet.methods
        .mint(to, poolId, amount, ctx.web3.utils.utf8ToHex(""))
        .send({ from: ctx.account }),
    { ...commonProps }
  );

  const poolMintBatch = useMutation(
    ({
      to,
      poolId,
      amount,
    }: {
      to: string[];
      poolId: string;
      amount: string[];
    }) =>
      terminusFacet.methods
        .poolMintBatch(poolId, to, amount)
        .send({ from: ctx.account }),
    { ...commonProps }
  );

  const mintBatch = useMutation(
    ({
      to,
      poolId,
      amount,
    }: {
      to: string;
      poolId: string[];
      amount: string[];
    }) =>
      terminusFacet.methods
        .mintBatch(to, poolId, amount, ctx.web3.utils.utf8ToHex(""))
        .send({ from: ctx.account }),
    { ...commonProps }
  );

  const withdrawPayments = useMutation(
    ({ to, amount }: { to: string; amount: string }) =>
      terminusFacet.methods
        .withdrawPayments(to, amount)
        .send({ from: ctx.account }),
    { ...commonProps }
  );

  const poolURI = useURI({ link: poolState.data?.uri });
  const contractJSON = useURI({ link: contractState.data?.contractURI });

  return {
    contractState,
    paymentToken,
    setURI,
    setPoolBasePrice,
    setPaymentToken,
    setController,
    newPool,
    poolState,
    balanceOf,
    setPoolURI,
    poolURI,
    setPoolController,
    mint,
    poolMintBatch,
    mintBatch,
    withdrawPayments,
    contractJSON,
  };
};

export default useTerminusContract;
