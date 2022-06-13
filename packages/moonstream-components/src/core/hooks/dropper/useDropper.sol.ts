import { useMutation, useQuery } from "react-query";
import {
  claimDrop,
  getClaim,
  getState,
  getSignerForClaim,
} from "../../contracts/dropper.contract";
import { MoonstreamWeb3ProviderInterface } from "../../../../../../types/Moonstream";
import queryCacheProps from "../hookCommon";
import useToast from "../useToast";
import useURI from "../useLink";
import { Dropper } from "../../../../../../types/contracts/Dropper";
const dropperAbi = require("../../../../../../abi/Dropper.json");
const useDropperContract = ({
  dropperAddress,
  ctx,
  claimId,
}: {
  dropperAddress?: string;
  ctx: MoonstreamWeb3ProviderInterface;
  claimId?: string;
}) => {
  const toast = useToast();

  const dropperContract = new ctx.web3.eth.Contract(
    dropperAbi
  ) as any as Dropper;
  dropperContract.options.address = dropperAddress ?? "";

  const _getClaim = async (
    dropperAddress: string,
    ctx: MoonstreamWeb3ProviderInterface,
    claimId: string
  ) => {
    let canClaim = false;
    const response = await getClaim(dropperAddress, ctx)(claimId);

    if (Number(response.status) > 0 || response.claim[0] == "0")
      canClaim = false;
    else canClaim = true;

    return { canClaim, ...response };
  };

  const claimState = useQuery(
    [
      "dropperContract",
      "claimState",
      dropperAddress,
      ctx.targetChain?.chainId,
      claimId,
    ],
    () => _getClaim(dropperAddress ?? "", ctx, claimId ?? ""),
    {
      ...queryCacheProps,
      onSuccess: () => {},
      // placeholderData: {
      //   canClaim: false,
      //   claim: ["", "", "", ""],
      //   status: "",
      //   claimUri: "",
      //   signer: "",
      // },
      enabled:
        !!dropperAddress &&
        ctx.web3?.utils.isAddress(ctx.account) &&
        !!ctx.chainId &&
        ctx.chainId === ctx.targetChain?.chainId &&
        !!claimId,
    }
  );

  const claimWeb3Drop = useMutation(claimDrop(dropperAddress, ctx), {
    onSuccess: () => {
      toast("Claim successful!", "success");
    },
    onError: (err: any) => {
      console.error(err);
      toast("Web3 call failed >_<", "error");
    },
  });

  const contractState = useQuery(
    ["dropperContract", "state", dropperAddress, ctx.targetChain?.chainId],
    () => getState(dropperAddress, ctx)(),
    {
      ...queryCacheProps,
      onSuccess: () => {},
      enabled:
        !!dropperAddress &&
        ctx.web3?.utils.isAddress(ctx.account) &&
        !!ctx.chainId &&
        ctx.chainId === ctx.targetChain?.chainId,
    }
  );

  const signerForClaim = useQuery(
    ["signerForClaim", dropperAddress, ctx.targetChain?.name, claimId],
    () => getSignerForClaim(dropperAddress, ctx)(claimId ?? ""),
    {
      ...queryCacheProps,
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) &&
        !!ctx.chainId &&
        !!claimId &&
        !!dropperAddress &&
        !!ctx.chainId &&
        ctx.targetChain?.chainId === ctx.chainId,
    }
  );

  const commonProps = {
    onSuccess: () => {
      toast("Successfully updated contract", "success");
      claimState.refetch();
    },
    onError: () => {
      toast("Something went wrong", "error");
    },
  };

  const setClaimURI = useMutation(
    ({ uri }: { uri: string }) =>
      dropperContract.methods
        .setClaimUri(claimId ?? "", uri)
        .send({ from: ctx.account }),
    { ...commonProps }
  );

  const setClaimSigner = useMutation(
    ({ signer }: { signer: string }) =>
      dropperContract.methods
        .setSignerForClaim(claimId ?? "", signer)
        .send({ from: ctx.account }),
    { ...commonProps }
  );

  const transferOwnership = useMutation(
    ({ to }: { to: string }) =>
      dropperContract.methods.transferOwnership(to).send({ from: ctx.account }),
    { ...commonProps }
  );

  const claimUri = useURI({ link: claimState.data?.claimUri });

  return {
    claimState,
    claimWeb3Drop,
    contractState,
    signerForClaim,
    claimUri,
    setClaimURI,
    setClaimSigner,
    transferOwnership,
  };
};

export default useDropperContract;
