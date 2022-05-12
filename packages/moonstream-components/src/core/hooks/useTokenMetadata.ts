import React from "react";

import { useMutation, useQuery } from "react-query";

import {
    ChainInterface,
    MoonstreamWeb3ProviderInterface,
} from "../../../../../types/Moonstream";

const useTokenMetadata = ({
    tokenURI,
}: {
    tokenURI: string;
}) => {
    const metadata = useQuery(
        ["TokenMetadata", tokenURI],
        () => fetch(tokenURI).then(res => res.json()),
        {
            onSuccess: () => { },
        }
    );

    return {
        metadata,
    };
}

export default useTokenMetadata;


