import { useMutation, useQuery } from "react-query";
import {
  claimDrop,
  getClaim,
  getState,
  getSignerForClaim,
} from "../../contracts/dropper.contract";
import {
  ChainInterface,
  MoonstreamWeb3ProviderInterface,
} from "../../../../../../types/Moonstream";
import queryCacheProps from "../hookCommon";
import useToast from "../useToast";

const useDropperContract = ({
  dropperAddress,
  ctx,
  claimId,
  targetChain,
}: {
  dropperAddress?: string;
  targetChain: ChainInterface;
  ctx: MoonstreamWeb3ProviderInterface;
  claimId?: string;
}) => {
  const toast = useToast();

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
    ["dropperContractClaimState", dropperAddress, targetChain.chainId, claimId],
    () => _getClaim(dropperAddress ?? "", ctx, claimId ?? ""),
    {
      ...queryCacheProps,
      onSuccess: () => {},
      placeholderData: {
        canClaim: false,
        claim: ["", "", "", ""],
        status: "",
      },
      enabled:
        !!dropperAddress &&
        ctx.web3?.utils.isAddress(ctx.account) &&
        !!ctx.chainId &&
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

  const dropperWeb3State = useQuery(
    ["dropperContractState", dropperAddress, targetChain.chainId],
    () => getState(dropperAddress, ctx)(),
    {
      ...queryCacheProps,
      onSuccess: () => {},
      enabled:
        !!dropperAddress &&
        ctx.web3?.utils.isAddress(ctx.account) &&
        ctx.chainId === ctx.chainId,
    }
  );

  const signerForClaim = useQuery(
    ["signerForClaim", dropperAddress, targetChain.name, claimId],
    () => getSignerForClaim(dropperAddress, ctx)(claimId ?? ""),
    {
      ...queryCacheProps,
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) &&
        !!ctx.chainId &&
        !!claimId &&
        !!dropperAddress &&
        !!targetChain.name,
    }
  );

  return { claimState, claimWeb3Drop, dropperWeb3State, signerForClaim };
};

export default useDropperContract;
