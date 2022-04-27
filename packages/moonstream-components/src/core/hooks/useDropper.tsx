import React from "react";
import { getDropList } from "../services/moonstream-engine.service";
import { useQuery } from "react-query";
import { getState } from "../contracts/dropper.contract";
import {
  ChainInterface,
  MoonstreamWeb3ProviderInterface,
} from "../../../../../types/Moonstream";

const useDropper = ({
  dropperAddress,
  targetChain,
  ctx,
}: {
  dropperAddress: string;
  targetChain: ChainInterface;
  ctx: MoonstreamWeb3ProviderInterface;
}) => {
  const dropperWeb3State = useQuery(
    ["dropperContractState", dropperAddress, targetChain.chainId],
    () => getState(dropperAddress, ctx)(),
    {
      onSuccess: () => {},
      enabled:
        ctx.web3?.utils.isAddress(ctx.account) && ctx.chainId === ctx.chainId,
    }
  );

  const dropList = useQuery(
    ["dropList", dropperAddress, targetChain.chainId],
    () => getDropList(dropperAddress, ctx)().then((data) => data.data.drops),
    {
      onSuccess: () => {},
    }
  );

  // const [usersDropList, setUsersDropList] = React.useState<Array<any>>([]);

  let usersDropList: any = {};
  usersDropList["data"] = React.useMemo((): any => {
    const retval: Array<any> = [];
    if (dropList?.data && ctx.account) {
      dropList.data.forEach((entry: any, id: Number) => {
        if (entry?.content?.includes(ctx.account)) {
          const claimIdtag = entry.tags.find((tag: string) =>
            tag.startsWith("claim_id:")
          );
          id = claimIdtag.split(":")[1];
          retval.push({ id, entry });
        }
      });
    }
    return retval;
  }, [dropList.data, ctx.account]);

  usersDropList.isLoading = dropList.isLoading;
  usersDropList.error = dropList.error;
  usersDropList.status = dropList.status;

  return { dropperWeb3State, usersDropList, dropList };
};

export default useDropper;
