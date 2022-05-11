import React from "react";

import { useMutation, useQuery } from "react-query";

import {
    ChainInterface,
    MoonstreamWeb3ProviderInterface,
} from "../../../../../types/Moonstream";
import { useToast } from ".";
import { getLootboxState } from "../contracts/lootbox.contract";

const useLootbox = ({
    contractAddress,
    lootboxId,
    targetChain,
    ctx,
}: {
    contractAddress: string;
    lootboxId: number;
    targetChain: ChainInterface;
    ctx: MoonstreamWeb3ProviderInterface;
}) => {
    const toast = useToast();

    const state = useQuery(
        ["LootboxState", contractAddress, targetChain.chainId, lootboxId],
        () => getLootboxState(contractAddress, ctx, lootboxId)(),
        {
            onSuccess: () => { },
            initialData: {
                lootboxUri: "",
                lootboxBalance: "",
            },
            enabled:
                ctx.web3?.utils.isAddress(ctx.account) &&
                ctx.chainId === targetChain.chainId,
        }
    );


    return {
        state,
    };
};

export default useLootbox;
